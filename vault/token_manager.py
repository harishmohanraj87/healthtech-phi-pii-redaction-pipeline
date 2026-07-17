import secrets
import string

def generate_token(entity_type: str) -> str:
    """
    Generates a secure, random token for a given entity type.
    Example input: 'NAME' -> Example output: '[NAME_A7f9X2]'
    """
    # Generate a 6-character secure random alphanumeric string
    alphabet = string.ascii_letters + string.digits
    random_suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
    
    # Format the token clearly so it is easy to identify in text
    token = f"[{entity_type.upper()}_{random_suffix}]"
    return token

# Quick verification test execution
if __name__ == "__main__":
    print("🛡️ Testing Token Generator...")
    
    # Simulate generating tokens for different types of sensitive data
    sample_name_token = generate_token("NAME")
    sample_phone_token = generate_token("PHONE")
    sample_email_token = generate_token("EMAIL")
    
    print(f"Generated Name Token:  {sample_name_token}")
    print(f"Generated Phone Token: {sample_phone_token}")
    print(f"Generated Email Token: {sample_email_token}")