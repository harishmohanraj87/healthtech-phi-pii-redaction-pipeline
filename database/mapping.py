import redis
import sys
import os
import time

# Allow Python to find the logger folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger.audit_logger import log_token_creation, log_token_retrieval

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connection Pooling for high-traffic production environments
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, max_connections=50)
redis_client = redis.Redis(connection_pool=pool)

def save_placeholder_mapping(token_placeholder: str, real_data: str, ttl_seconds: int = 3600):
    """
    Saves mapping with TTL. Includes production error handling for database outages.
    """
    start_time = time.time()
    try:
        redis_client.set(token_placeholder, real_data, ex=ttl_seconds)
        latency_ms = (time.time() - start_time) * 1000
        log_token_creation("PHI_DATA", token_placeholder)
        return latency_ms
        
    except redis.exceptions.ConnectionError:
        print("⚠️ ERROR: Could not connect to the database. Is Redis running?")
        return -1.0 # Return a negative latency to indicate failure

def get_real_data(token_placeholder: str):
    """
    Retrieves original data safely. Returns (data, latency_ms).
    """
    start_time = time.time()
    try:
        data = redis_client.get(token_placeholder)
        latency_ms = (time.time() - start_time) * 1000
        
        if data:
            log_token_retrieval(token_placeholder, success=True)
            return data, latency_ms
        else:
            log_token_retrieval(token_placeholder, success=False)
            return None, latency_ms
            
    except redis.exceptions.ConnectionError:
        print("⚠️ ERROR: Database connection refused during retrieval.")
        return None, -1.0

# Quick verification test execution
if __name__ == "__main__":
    sample_token = "TOKEN_PROD_123"
    sample_data = "John Doe / 555-0199"
    
    save_latency = save_placeholder_mapping(sample_token, sample_data)
    retrieved_data, fetch_latency = get_real_data(sample_token)
    
    if save_latency != -1.0:
        print(f"✅ Save Latency: {save_latency:.2f} ms")
        print(f"✅ Fetch Latency: {fetch_latency:.2f} ms")
        print(f"✅ Retrieved Data: {retrieved_data}")