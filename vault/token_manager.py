import secrets
import string
import sys
import os
import time

# Allow Python to find the logger folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger.audit_logger import log_token_creation

def generate_token(entity_type: str):
    """
    Generates a secure, random token and returns a tuple: (token, latency_ms).
    """
    start_time = time.time()
    
    alphabet = string.ascii_letters + string.digits
    random_suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
    token = f"[{entity_type.upper()}_{random_suffix}]"
    
    log_token_creation(entity_type, token)
    
    # Calculate exactly how fast this function ran
    latency_ms = (time.time() - start_time) * 1000
    
    return token, latency_ms

# Production-ready verification test
if __name__ == "__main__":
    sample_token, gen_latency = generate_token("DISEASE")
    print(f"✅ Generated Token: {sample_token}")
    print(f"✅ Vault Execution Latency: {gen_latency:.2f} ms")