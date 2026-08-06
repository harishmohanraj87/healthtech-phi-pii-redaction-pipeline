import os
import sys
import time

import redis

# Allow Python to find the logger folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.audit_logger import (
    log_token_creation,
    log_token_retrieval,
)

# --------------------------------------------------------------------
# Redis Configuration
# --------------------------------------------------------------------

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# --------------------------------------------------------------------
# Redis Connection Pool
# --------------------------------------------------------------------

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    max_connections=50,
)

redis_client = redis.Redis(
    connection_pool=pool
)

# --------------------------------------------------------------------
# Save Mapping
# --------------------------------------------------------------------

def save_placeholder_mapping(
    token_placeholder: str,
    real_data: str,
    ttl_seconds: int = 3600,
):
    """
    Save a placeholder → original PHI mapping in Redis.
    Returns latency (ms).
    """

    start_time = time.perf_counter()

    try:
        redis_client.set(
            token_placeholder,
            real_data,
            ex=ttl_seconds,
        )

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        log_token_creation(
            "PHI_DATA",
            token_placeholder,
        )

        return latency_ms

    except redis.exceptions.ConnectionError:

        print(
            "⚠️ ERROR: Could not connect to Redis."
        )

        return -1.0


# --------------------------------------------------------------------
# Retrieve Mapping
# --------------------------------------------------------------------

def get_real_data(token_placeholder: str):
    """
    Retrieve the original PHI value.

    Returns:
        (data, latency_ms)
    """

    start_time = time.perf_counter()

    try:

        data = redis_client.get(
            token_placeholder
        )

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        if data:

            log_token_retrieval(
                token_placeholder,
                success=True,
            )

            return data, latency_ms

        log_token_retrieval(
            token_placeholder,
            success=False,
        )

        return None, latency_ms

    except redis.exceptions.ConnectionError:

        print(
            "⚠️ ERROR: Redis connection refused."
        )

        return None, -1.0


# --------------------------------------------------------------------
# Manual Verification
# --------------------------------------------------------------------

if __name__ == "__main__":

    sample_token = "TOKEN_PROD_123"
    sample_data = "John Doe / 555-0199"

    save_latency = save_placeholder_mapping(
        sample_token,
        sample_data,
    )

    retrieved_data, fetch_latency = get_real_data(
        sample_token
    )

    if save_latency != -1.0:

        print(f"✅ Save Latency : {save_latency:.2f} ms")
        print(f"✅ Fetch Latency: {fetch_latency:.2f} ms")
        print(f"✅ Retrieved    : {retrieved_data}")