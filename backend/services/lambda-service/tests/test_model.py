import uuid
from unittest.mock import Mock, patch

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


import importlib


def test_upload_download_delete_s3_success_and_failure(monkeypatch):
    inst = DummyModel()

    # Mock successful put_object
    mock_s3 = Mock()
    mock_s3.put_object.return_value = {}
    # Patch the AWS services module
    mod_aws_services = importlib.import_module("lib.aws")
    
    # Mock get_s3() to return our mock client
    monkeypatch.setattr(mod_aws_services, "get_s3", lambda: mock_s3)

    key = inst._upload_to_s3("file", b"data")
    assert key is not None
    assert "dummy-table/file/" in key
    mock_s3.put_object.assert_called_once()

    # Mock get_object returning a body with read()
    body = Mock()
    body.read.return_value = b"data"
    mock_s3.get_object.return_value = {"Body": body}
    data = inst._download_from_s3(key)
    assert data == b"data"

    # Mock delete_object success
    mock_s3.delete_object.return_value = {}
    ok = inst._delete_from_s3(key)
    assert ok is True

    # Simulate s3 errors
    def raise_client_error(*a, **k):
        raise make_client_error()

    mock_s3.put_object.side_effect = raise_client_error
    bad = inst._upload_to_s3("file", b"data")
    assert bad is None

    mock_s3.get_object.side_effect = raise_client_error
    assert inst._download_from_s3(key) is None

    mock_s3.delete_object.side_effect = raise_client_error
    assert inst._delete_from_s3(key) is False


def test_save_put_item_and_s3_handling(monkeypatch):
    # Prepare model with bytes in s3 field
    inst = DummyModel(id="1", file=b"bytesdata", other="x")

    # Patch _upload_to_s3 to return a key
    monkeypatch.setattr(DummyModel, "_upload_to_s3", lambda self, f, d: "k123")

    mock_table = Mock()
    mock_table.put_item.return_value = {}
    # Patch table() to return our mock
    monkeypatch.setattr(DummyModel, "table", classmethod(lambda cls: mock_table))

    assert inst.save() is True
    # ensure put_item was called with item that contains file_s3_key and not file
    called_item = mock_table.put_item.call_args[1]["Item"]
    assert "file_s3_key" in called_item
    assert "file" not in called_item

    # If upload fails (returns None) save should return False
    monkeypatch.setattr(DummyModel, "_upload_to_s3", lambda self, f, d: None)
    assert inst.save() is False

    # If put_item raises ClientError, save should return False
    monkeypatch.setattr(DummyModel, "_upload_to_s3", lambda self, f, d: "k123")
    def raise_err(*args, **kwargs):
        raise make_client_error()

    mock_table.put_item.side_effect = raise_err
    assert inst.save() is False


def test_get_load_s3_data_and_clienterror(monkeypatch):
    # Setup item returned from DynamoDB
    item = {"id": "1", "file_s3_key": "k123"}

    mock_table = Mock()
    mock_table.get_item.return_value = {"Item": item}
    monkeypatch.setattr(DummyModel, "table", classmethod(lambda cls: mock_table))

    # Patch _download_from_s3 to return bytes when loading
    monkeypatch.setattr(DummyModel, "_download_from_s3", lambda self, k: b"blob")

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


def test_get_file_and_url_and_validation(monkeypatch):
    inst = DummyModel(id="1")

    # field not present in s3_fields -> ValueError
    with pytest.raises(ValueError):
        inst.get_file("not-a-field")

    # No s3 key -> None
    assert inst.get_file("file") is None

    # Provide s3 key and patch download
    inst.file_s3_key = "k1"
    monkeypatch.setattr(DummyModel, "_download_from_s3", lambda self, k: b"b")
    assert inst.get_file("file") == b"b"

    # get_file_url validation
    with pytest.raises(ValueError):
        inst.get_file_url("not-a-field")

    # no s3 key -> None
    inst2 = DummyModel(id="2")
    with pytest.raises(ValueError):
        inst2.get_file_url("not-a-field")

    inst.file_s3_key = "k1"
    mock_s3 = Mock()
    mock_s3.generate_presigned_url.return_value = "https://signed"
    mod_aws_services = importlib.import_module("lib.aws")
    
    # Mock get_s3() to return our mock client
    monkeypatch.setattr(mod_aws_services, "get_s3", lambda: mock_s3)
    
    url = inst.get_file_url("file", expires_in=10)
    assert url == "https://signed"

    # presign failure
    def raise_err(*a, **k):
        raise make_client_error()

    mock_s3.generate_presigned_url.side_effect = raise_err
    assert inst.get_file_url("file") is None


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
    monkeypatch.setattr(DummyModel, "table", classmethod(lambda cls: mock_table))

    assert inst.delete() is True
    assert called['k'] == "k1"

    # If delete_item raises error, delete should return False
    def raise_err(*a, **k):
        raise make_client_error()

    mock_table.delete_item.side_effect = raise_err
    assert inst.delete() is False
