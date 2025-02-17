from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config.collections import METADATA_COLLECTION
from config.mongo_db import MongoDBManager

class MetadataService:
    """
    Service class to store and retrieve metadata from MongoDB.
    """
    def __init__(self):
        """
        Initialize the MetadataService with a MongoDB connection.
        """
        manager=MongoDBManager()
        self.collection =manager.get_collection(METADATA_COLLECTION)

    def set_metadata(self, metadata_type, value):
        """
        Store or update a metadata entry in MongoDB.
        
        :param metadata_type: The metadata type (e.g., "start_email_id").
        :param value: The metadata value to store.
        """
        try:
            # Try to update the existing metadata
            result = self.collection.update_one(
                {"type": metadata_type},
                {"$set": {"value": value}},
                upsert=True  # If the document doesn't exist, create it
            )
            if result.matched_count > 0:
                print(f"Metadata updated for type: {metadata_type}")
            else:
                print(f"Metadata inserted for type: {metadata_type}")
        except PyMongoError as e:
            print(f"Failed to set metadata: {e}")

    def get_metadata(self, metadata_type):
        """
        Retrieve metadata by its type from MongoDB.
        
        :param metadata_type: The metadata type to search for (e.g., "start_email_id").
        :return: The metadata value or None if not found.
        """
        try:
            metadata = self.collection.find_one({"type": metadata_type})
            return metadata["value"] if metadata else None
        except PyMongoError as e:
            print(f"Failed to get metadata: {e}")
            return None

    def delete_metadata(self, metadata_type):
        """
        Delete a metadata entry from MongoDB by its type.
        
        :param metadata_type: The metadata type to delete (e.g., "start_email_id").
        """
        try:
            result = self.collection.delete_one({"type": metadata_type})
            if result.deleted_count > 0:
                print(f"Metadata deleted for type: {metadata_type}")
            else:
                print(f"No metadata found for type: {metadata_type}")
        except PyMongoError as e:
            print(f"Failed to delete metadata: {e}")
