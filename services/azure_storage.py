# services/azure_storage.py
import os
from azure.storage.blob import BlobServiceClient

class AzureStorage:
    def __init__(self):
        AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

        if not AZURE_STORAGE_CONNECTION_STRING or not AZURE_CONTAINER_NAME:
            raise ValueError("Azure Storage environment variables are not set")

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
        return blob_client.url
