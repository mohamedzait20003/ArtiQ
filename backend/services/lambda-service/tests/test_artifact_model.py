from unittest.mock import Mock

from app.models.Artifact_Model import Artifact_Model


def test_primary_key_and_init():
    a = Artifact_Model(
        id="i1", name="n", artifact_type="model", source_url="u"
    )
    assert a.id == "i1"
    assert a.name == "n"
    assert a.artifact_type == "model"
    assert a.source_url == "u"
    assert Artifact_Model.primary_key() == ["id"]


def test_scan_artifacts_no_filters(monkeypatch):
    mock_collection = Mock()
    mock_cursor = [
        {
            "id": "1",
            "name": "one",
            "artifact_type": "model",
            "source_url": "u1"
        },
        {
            "id": "2",
            "name": "two",
            "artifact_type": "dataset",
            "source_url": "u2"
        },
    ]
    
    # Mock find().limit() to return cursor
    mock_find = Mock()
    mock_find.limit.return_value = mock_cursor
    mock_collection.find.return_value = mock_find

    # patch collection() to return our mock
    monkeypatch.setattr(
        Artifact_Model, "collection", classmethod(lambda cls: mock_collection)
    )

    res = Artifact_Model.scan_artifacts()

    assert isinstance(res, dict)
    assert len(res["items"]) == 2
    assert res["last_evaluated_key"] is None
    # ensure returned items are Artifact_Model instances
    assert all(isinstance(x, Artifact_Model) for x in res["items"])


def test_scan_with_limit_and_exclusive_start_key(monkeypatch):
    mock_collection = Mock()
    mock_cursor = []
    
    # Mock find().limit() to return cursor
    mock_find = Mock()
    mock_find.limit.return_value = mock_cursor
    mock_collection.find.return_value = mock_find
    
    monkeypatch.setattr(
        Artifact_Model, "collection", classmethod(lambda cls: mock_collection)
    )

    res = Artifact_Model.scan_artifacts(
        limit=5, exclusive_start_key={"id": "10"}
    )

    # verify find was called and limit was applied
    mock_collection.find.assert_called_once()
    mock_find.limit.assert_called_once_with(5)
    assert res["items"] == []


def test_scan_with_name_and_types_filter(monkeypatch):
    mock_collection = Mock()
    mock_cursor = [
        {
            "id": "1",
            "name": "foo",
            "artifact_type": "model",
            "source_url": "u"
        }
    ]
    
    # Mock find().limit() to return cursor
    mock_find = Mock()
    mock_find.limit.return_value = mock_cursor
    mock_collection.find.return_value = mock_find
    
    monkeypatch.setattr(
        Artifact_Model, "collection", classmethod(lambda cls: mock_collection)
    )

    res = Artifact_Model.scan_artifacts(
        name_filter="foo", types_filter=["model", "badtype"]
    )

    # find should be called with a query filter
    mock_collection.find.assert_called_once()
    call_args = mock_collection.find.call_args[0][0]
    assert 'name' in call_args
    assert call_args['name'] == 'foo'
    assert len(res["items"]) == 1


def test_scan_handles_exception(monkeypatch):
    mock_table = Mock()

    def raise_err(*a, **k):
        raise RuntimeError("boom")

    mock_table.scan.side_effect = raise_err
    monkeypatch.setattr(
        Artifact_Model, "collection", classmethod(lambda cls: mock_table)
    )

    res = Artifact_Model.scan_artifacts()
    assert res["items"] == []
    assert res["last_evaluated_key"] is None
