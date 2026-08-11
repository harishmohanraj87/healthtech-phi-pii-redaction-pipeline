from vault.token_vault import TokenVault

vault = TokenVault()

token = vault.get_or_create_token("PERSON", "John Doe")

print("Generated Token:", token)

original = vault.restore_token(token)

print("Restored Value:", original)