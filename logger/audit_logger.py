import logging
import os

# Create a logs folder automatically if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure the logger to save to a file
logging.basicConfig(
    filename='logs/audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_token_creation(entity_type: str, token: str):
    """Logs when a new secure token is generated."""
    logging.info(f"SECURE ACTION: Token created for entity [{entity_type}]. Token ID: {token}")

def log_token_retrieval(token: str, success: bool):
    """Logs when the pipeline attempts to reverse-map a token."""
    if success:
        logging.info(f"ACCESS GRANTED: Successful retrieval for Token ID: {token}")
    else:
        logging.warning(f"ACCESS DENIED/FAILED: Retrieval attempt for Token ID: {token} - Token expired or invalid")