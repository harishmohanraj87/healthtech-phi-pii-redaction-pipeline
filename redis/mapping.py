import redis

# 1. Connect to the local Redis instance running in Docker
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def test_connection():
    try:
        # Ping the Redis server to check if it's alive
        if redis_client.ping():
            print("🚀 Connected to Redis successfully!")
    except redis.ConnectionError:
        print("❌ Could not connect to Redis. Is the Docker container running?")

def save_placeholder_mapping(token_placeholder: str, real_data: str):
    """
    Saves the mapping of a token/placeholder to the actual sensitive data.
    """
    # Using a 1-hour expiration time (3600 seconds) for security/session handling
    redis_client.set(token_placeholder, real_data, ex=3600)
    print(f"Stored mapping: {token_placeholder} -> [PROTECTED DATA]")

def get_real_data(token_placeholder: str) -> str:
    """
    Retrieves the original sensitive data using the placeholder token.
    (This is your 'Reverse Mapping')
    """
    return redis_client.get(token_placeholder)

# Quick verification test execution
if __name__ == "__main__":
    test_connection()
    
    # Simulate saving a tokenized placeholder
    sample_token = "TOKEN_XYZ_12345"
    sample_sensitive_data = "John Doe / 98765-43210"
    
    # Test mapping
    save_placeholder_mapping(sample_token, sample_sensitive_data)
    
    # Test reverse mapping
    retrieved_data = get_real_data(sample_token)
    print(f"Retrieved original data: {retrieved_data}")