from app.security import create_access_token, decode_access_token

def test_access_token_roundtrip():
    token = create_access_token(123)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
