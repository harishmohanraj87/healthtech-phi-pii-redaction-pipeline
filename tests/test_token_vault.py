"""
test_token_vault.py

Unit tests for the Redis-backed Token Vault.
"""

from vault.token_vault import TokenVault


def test_same_value_returns_same_token():
    """
    The same PHI value should always return
    the same secure token.
    """

    vault = TokenVault()

    token1 = vault.get_or_create_token(
        "PERSON",
        "John Doe"
    )

    token2 = vault.get_or_create_token(
        "PERSON",
        "John Doe"
    )

    assert token1 == token2


def test_different_values_return_different_tokens():
    """
    Different PHI values should generate
    different secure tokens.
    """

    vault = TokenVault()

    token1 = vault.get_or_create_token(
        "PERSON",
        "John Doe"
    )

    token2 = vault.get_or_create_token(
        "PERSON",
        "Jane Smith"
    )

    assert token1 != token2


def test_restore_original_value():
    """
    Verify reverse lookup from
    Token -> Original PHI.
    """

    vault = TokenVault()

    token = vault.get_or_create_token(
        "EMAIL",
        "john@example.com"
    )

    original = vault.restore_token(token)

    assert original == "john@example.com"