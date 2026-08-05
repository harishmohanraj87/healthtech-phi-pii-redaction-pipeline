from infrastructure.redis_client import RedisClient
from vault.token_manager import generate_token


class TokenVault:
    """
    Redis-backed Token Vault.

    Responsibilities:
    - Store original PHI values with generated tokens.
    - Return the same token if the value already exists.
    - Restore original values from tokens.
    """

    def __init__(self):
        self.redis = RedisClient().client

    def get_or_create_token(self, entity_type: str, original_value: str) -> str:
        """
        Returns an existing token if the value has already been stored.
        Otherwise generates a new token and stores the mapping.
        """

        lookup_key = f"lookup:{entity_type}:{original_value}"

        # Check if we already have a token for this value
        existing_token = self.redis.get(lookup_key)

        if existing_token:
            return existing_token

        # Generate a new token
        token, latency_ms = generate_token(entity_type)

        # Store forward mapping
        self.redis.set(lookup_key, token)

        # Store reverse mapping
        self.redis.set(token, original_value)

        print(f"✅ Token generated in {latency_ms:.2f} ms")

        return token

    def restore_token(self, token: str):
        """
        Restore the original value from a token.
        """

        return self.redis.get(token)