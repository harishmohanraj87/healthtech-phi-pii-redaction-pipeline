import logging

# Configure production-ready logging with exact timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [AUDIT] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_token_creation(entity_type: str, token: str) -> None:
    """
    Logs the generation of a new secure token.
    """
    logger.info(f"Token created for entity: {entity_type} | Token ID: {token}")

def log_token_retrieval(token: str, success: bool) -> None:
    """
    Logs the attempt to reverse-map a token back to original data.
    """
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Token retrieval attempt: {token} | Status: {status}")