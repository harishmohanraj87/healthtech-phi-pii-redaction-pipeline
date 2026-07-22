import secrets
import string
import sys
import os

# Allow Python to find the logger folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger.audit_logger import log_token_creation

def generate_token(entity_type: str) -> str:
    """
    Generates a secure, random token for a given entity type and logs the creation.
    """
    alphabet = string.ascii_letters + string.digits
    random_suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
    
    token = f"[{entity_type.upper()}_{random_suffix}]"
    
    # NEW: Log the creation of the token
    log_token_creation(entity_type, token)
    
    return token

if __name__ == "__main__":
    print("🛡️ Testing Token Generator with Logging...")
    sample_name_token = generate_token("NAME")
    print(f"Generated and logged: {sample_name_token}")