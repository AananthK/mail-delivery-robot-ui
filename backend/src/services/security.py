# security.py: module strictly for password handling

from passlib.context import CryptContext

# password hashing manager: chooses algorithm
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],  # prefer argon2, allow bcrypt
    deprecated="auto",
)

# take a password and hash it with salting
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# compare a password to its hash to verify it
def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
