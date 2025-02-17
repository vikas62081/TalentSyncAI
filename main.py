import os
import uvicorn
import argparse
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Command line argument parsing
parser = argparse.ArgumentParser(description="Run FastAPI server.")
parser.add_argument("--env", type=str, default="dev", help="Set the environment (dev or prod).")
args = parser.parse_args()

# Determine environment and load corresponding .env file
environment = args.env
env_file_name = ".env.dev" if environment == "dev" else ".env.prod"

# Load the environment variables from the appropriate file
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, env_file_name))

# Adjust logging level based on environment
if environment == "prod":
    logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors in production
else:
    logging.basicConfig(level=logging.DEBUG)  # Show debug logs in development

logger.info(f"\n\nStarting the application in {environment} environment.\n\n")

if environment == "dev":
    logger.debug("Debugging information enabled.")
    

# Start the FastAPI application with Uvicorn
if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=(environment != "prod"))

