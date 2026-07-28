import redis
import sys
import os
import time

# Allow Python to find the logger folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger.audit_logger import log_token_creation, log_token_retrieval

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# WEEK 3 OPTIMIZATION: Connection Pooling for high-traffic production environments
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, max_connections=50)
redis_client = redis.Redis(connection_pool=pool)

def save_placeholder_mapping(token_placeholder: str, real_data: str, ttl_seconds: int = 3600) -> float:
    """
    Saves mapping with TTL and returns the execution latency in milliseconds.
    """
    start_time = time.time()
    redis_client.set(token_placeholder, real_data, ex=ttl_seconds)
    latency_ms = (time.time() - start_time) * 1000
    
    log_token_creation("PHI_DATA", token_placeholder)
    return latency_ms

def get_real_data(token_placeholder: str):
    """
    Retrieves original data and returns a tuple: (data, latency_ms).
    """
    start_time = time.time()
    data = redis_client.get(token_placeholder)
    latency_ms = (time.time() - start_time) * 1000
    
    if data:
        log_token_retrieval(token_placeholder, success=True)
        return data, latency_ms
    else:
        log_token_retrieval(token_placeholder, success=False)
        return None, latency_ms

# Quick verification test execution
if __name__ == "__main__":
    sample_token = "TOKEN_PROD_123"
    sample_data = "John Doe / 555-0199"
    
    save_latency = save_placeholder_mapping(sample_token, sample_data)
    # Testing the output format
    retrieved_data, fetch_latency = get_real_data(sample_token)
    
    print(f"✅ Save Latency: {save_latency:.2f} ms")
    print(f"✅ Fetch Latency: {fetch_latency:.2f} ms")
    print(f"✅ Retrieved Data: {retrieved_data}")