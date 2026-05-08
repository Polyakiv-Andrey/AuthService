import bcrypt

from src.utils.password import hash_password


def test_password():
    password = "strongpassword"
    hashed_password = hash_password(password)
    assert bcrypt.checkpw(password.encode(), hashed_password.encode())


def test_password_with_salt():
    password1 = "strongpassword"
    password2 = "strongpassword"
    hashed_password1 = hash_password(password1)
    hashed_password2 = hash_password(password2)
    assert hashed_password1 != hashed_password2
