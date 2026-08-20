import io
from unittest.mock import MagicMock, patch

from app.gateways.storage import StorageGateway


@patch("app.gateways.storage.boto3.client")
def test_put_object_delegates_to_s3_client(mock_boto_client) -> None:
    mock_client = MagicMock()
    mock_client.head_object.return_value = {"ContentLength": 42, "ContentType": "image/png"}
    mock_boto_client.return_value = mock_client

    gateway = StorageGateway()
    result = gateway.put_object("channels/1/thumb.png", io.BytesIO(b"data"), "image/png")

    mock_client.upload_fileobj.assert_called_once()
    assert result.storage_key == "channels/1/thumb.png"
    assert result.size_bytes == 42
    assert result.content_type == "image/png"


@patch("app.gateways.storage.boto3.client")
def test_object_exists_false_on_client_error(mock_boto_client) -> None:
    mock_client = MagicMock()

    class _ClientError(Exception):
        pass

    mock_client.exceptions.ClientError = _ClientError
    mock_client.head_object.side_effect = _ClientError()
    mock_boto_client.return_value = mock_client

    gateway = StorageGateway()

    assert gateway.object_exists("missing-key") is False
