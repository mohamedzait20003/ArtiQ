from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from app.models.Model import Model


class DummyModel(Model):
    table_name = "dummy-table"
    s3_bucket = "dummy-bucket"
    s3_fields = ["file"]

    @classmethod
    def primary_key(cls):
        return ["id"]


def make_client_error():
    return ClientError({"Error": {"Message": "boom", "Code": "500"}}, "Op")


def test_upload_download_delete_s3(monkeypatch):
    inst = DummyModel()

    # Moto handles actual S3 operations, test real behavior
    key = inst._upload_to_s3("file", b"data")
    assert key is not None
    assert "dummy-table/file/" in key

    # Test download from S3
    data = inst._download_from_s3(key)
    assert data == b"data"

    # Test delete from S3
    ok = inst._delete_from_s3(key)
    assert ok is True

    # Test error cases with non-existent bucket/key
    # Download from non-existent key
    bad_download = inst._download_from_s3("nonexistent-key")
    assert bad_download is None

    # Delete non-existent key (S3 delete is idempotent, returns True)
    ok_delete = inst._delete_from_s3("nonexistent-key")
    assert ok_delete is True


def test_save_put_item_and_s3_handling(monkeypatch):
    # Prepare model with bytes in s3 field
    inst = DummyModel(id="1", file=b"bytesdata", other="x")

    # Patch _upload_to_s3 to return a key
    monkeypatch.setattr(
        DummyModel, "_upload_to_s3", lambda self, f, d: "k123"
    )

    mock_table = Mock()
    mock_table.put_item.return_value = {}
    # Patch collection() to return our mock
    monkeypatch.setattr(
        DummyModel, "collection", classmethod(lambda cls: mock_table)
    )

    assert inst.save() is True

    called_item = mock_table.put_item.call_args[1]["Item"]
    assert "file_s3_key" in called_item
    assert "file" not in called_item

    # If upload fails (returns None) save should return False
    monkeypatch.setattr(
        DummyModel, "_upload_to_s3", lambda self, f, d: None
    )
    assert inst.save() is False

    # If put_item raises ClientError, save should return False
    monkeypatch.setattr(
        DummyModel, "_upload_to_s3", lambda self, f, d: "k123"
    )

    def raise_err(*args, **kwargs):
        raise make_client_error()

    mock_table.put_item.side_effect = raise_err
    assert inst.save() is False


def test_get_load_s3_data(monkeypatch):
    # Setup item returned from MongoDB
    item = {"id": "1", "file_s3_key": "k123"}

    mock_table = Mock()
    mock_table.get_item.return_value = {"Item": item}
    monkeypatch.setattr(
        DummyModel, "collection", classmethod(lambda cls: mock_table)
    )

    # Patch _download_from_s3 to return bytes when loading
    monkeypatch.setattr(
        DummyModel, "_download_from_s3", lambda self, k: b"blob"
    )

    inst = DummyModel.get({"id": "1"}, load_s3_data=True)
    assert isinstance(inst, DummyModel)
    assert inst.file == b"blob"

    # If no item present, get returns None
    mock_table.get_item.return_value = {}
    assert DummyModel.get({"id": "missing"}) is None

    # If table.get_item raises ClientError, get returns None
    def raise_err(*a, **k):
        raise make_client_error()

    mock_table.get_item.side_effect = raise_err
    assert DummyModel.get({"id": "1"}) is None


def test_get_file_and_url(monkeypatch):
    inst = DummyModel(id="1")

    # field not present in s3_fields -> ValueError
    with pytest.raises(ValueError):
        inst.get_file("not-a-field")

    # No s3 key -> None
    assert inst.get_file("file") is None

    # Provide s3 key and patch download
    inst.file_s3_key = "k1"
    monkeypatch.setattr(
        DummyModel, "_download_from_s3", lambda self, k: b"b"
    )
    assert inst.get_file("file") == b"b"

    # get_file_url validation
    with pytest.raises(ValueError):
        inst.get_file_url("not-a-field")

    # no s3 key -> None
    inst2 = DummyModel(id="2")
    with pytest.raises(ValueError):
        inst2.get_file_url("not-a-field")

    inst.file_s3_key = "k1"
    # Test presigned URL generation with moto (real S3 behavior)
    url = inst.get_file_url("file", expires_in=10)
    # Moto generates real presigned URLs, check it's valid
    assert url.startswith("https://dummy-bucket.s3.amazonaws.com/k1?")
    assert "X-Amz-Algorithm" in url
    assert "X-Amz-Expires=10" in url


def test_delete_calls_s3_and_table(monkeypatch):
    inst = DummyModel(id="1")
    inst.file_s3_key = "k1"

    # Patch _delete_from_s3 to record calls
    called = {}

    def fake_delete(self, key):
        called['k'] = key
        return True

    monkeypatch.setattr(DummyModel, "_delete_from_s3", fake_delete)

    mock_table = Mock()
    mock_table.delete_item.return_value = {}
    monkeypatch.setattr(
        DummyModel, "collection", classmethod(lambda cls: mock_table)
    )

    assert inst.delete() is True
    assert called['k'] == "k1"

    # If delete_item raises error, delete should return False
    def raise_err(*a, **k):
        raise make_client_error()

    mock_table.delete_item.side_effect = raise_err
    assert inst.delete() is False
