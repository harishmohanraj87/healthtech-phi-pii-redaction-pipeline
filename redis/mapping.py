import redis
import sys
import os

# Allow Python to find the logger folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger.audit_logger import log_token_creation, log_token_retrieval

# Connect to persistent Redis database
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def save_placeholder_mapping(token_placeholder: str, real_data: str, ttl_seconds: int = 3600):
    """
    Saves mapping with Session Handling (TTL). Default expiration is 1 hour.
    """
    # ex=ttl_seconds handles the session expiration automatically
    redis_client.set(token_placeholder, real_data, ex=ttl_seconds)
    
    # Log the action (NEVER log the real_data variable for privacy reasons)
    log_token_creation("PHI_DATA", token_placeholder)
    print(f"✅ Stored mapping securely. Session expires in {ttl_seconds} seconds.")

def get_real_data(token_placeholder: str) -> str:
    """
    Reverse Mapping: Retrieves original data with edge-case handling.
    """
    data = redis_client.get(token_placeholder)
    
    if data:
        # Token found, session is still active
        log_token_retrieval(token_placeholder, success=True)
        return data
    else:
        # Token not found or session has expired
        log_token_retrieval(token_placeholder, success=False)
        print("❌ Error: Token not found or session has expired.")
        return None

# Quick verification test execution
if __name__ == "__main__":
    sample_token = "TOKEN_XYZ_99999"
    sample_sensitive_data = "Jane Smith / 123-456-7890"
    
    # Test Saving
    save_placeholder_mapping(sample_token, sample_sensitive_data)
    
    # Test Retrieving
    retrieved = get_real_data(sample_token)
    print(f"Retrieved: {retrieved}")
    
    # Test Fake Token (Error Handling)
    print("\nTesting invalid token retrieval...")
    get_real_data("FAKE_TOKEN_000")