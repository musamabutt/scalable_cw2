# services/azure_storage.py
from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME

class AzureStorage:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        self.container_client = self.blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        try:
            self.container_client.create_container()
        except Exception:
            # container likely already exists
            pass

    def upload_file(self, file_bytes: bytes, filename: str) -> str:
        """
        Upload bytes to blob storage and return the blob URL.
        """
        blob_client = self.container_client.get_blob_client(filename)
        blob_client.upload_blob(file_bytes, overwrite=True)
        # blob_client.url is a URL to the blob
        return blob_client.url
