from pymongo import MongoClient
from urllib.parse import quote_plus
import logging

# MongoDB Configuration
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'thinklusive_marketing360'
MONGO_SUB_COL = 'users_submission'
MONGO_DB_USER = 'ubuntu'
MONGO_USER_PASS = 'thinklusive%402023'
username="simplified"
password="simplified123!"

uri = "mongodb+srv://"+username+":"+password+"@cluster0.s9z2dp0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
class MongoDBManager:
    """
    A singleton class to manage MongoDB connections and operations.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of the class is created.
        """
        if not cls._instance:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, host=MONGO_HOST, port=MONGO_PORT, db_name=MONGO_DB, username=MONGO_DB_USER, password=MONGO_USER_PASS):
        """
        Initializes the MongoDBManager with the given connection parameters.
        This method is only called once due to the singleton pattern.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.db_name = db_name
            self.client = self._create_client(host, port, username, password)
            self.db = self.client[db_name]
            self.current_collection = None
            logging.info(f"Connected to MongoDB database: {db_name}")

    def _create_client(self, host, port, username, password):
        """
        Creates a MongoDB client with authentication.
        
        Args:
            host (str): MongoDB host.
            port (int): MongoDB port.
            username (str): MongoDB username.
            password (str): MongoDB password.
            
        Returns:
            MongoClient: A MongoDB client instance.
        """
        try:
            if username and password:
                username = quote_plus(username)
                password = quote_plus(password)
                # uri = f"mongodb://{username}:{password}@{host}:{port}/{self.db_name}?authSource={self.db_name}"
                logging.debug(f"Connecting with URI: {uri}")
                return MongoClient(uri,tls=True, tlsAllowInvalidCertificates=True)
            else:
                logging.debug(f"Connecting without authentication to {host}:{port}")
                return MongoClient(host, port)
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def set_collection(self, collection_name):
        """
        Sets the current collection for database operations.
        
        Args:
            collection_name (str): The name of the collection.
        """
        self.current_collection = self.db[collection_name]
        logging.info(f"Current collection set to: {collection_name}")

    def get_collection(self, collection_name):
        """
        Retrieves a MongoDB collection.
        
        Args:
            collection_name (str): The name of the collection to retrieve.
        
        Returns:
            Collection: The MongoDB collection instance.
        """
        logging.info(f"Fetching collection: {collection_name}")
        return self.db[collection_name]

    def close_connection(self):
        """
        Closes the MongoDB client connection.
        """
        self.client.close()
        logging.info("MongoDB connection closed.")

