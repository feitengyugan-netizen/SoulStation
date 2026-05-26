"""Test what password was actually used for the existing hashes"""
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"])

# The existing hashes from the database
users_hash = "$2b$12$AzF8DWzmXNmKODeXrus77uZVR1QK7fUd35XAN5Z6cYnT6irzwKLFC"
admins_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i"

# Is it just a normal hash of '123456'?
print("1. Verify '123456' against users_hash:", pwd.verify("123456", users_hash))
print("2. Verify '123456' against admins_hash:", pwd.verify("123456", admins_hash))

# Maybe it was hashed with bcrypt.checkpw directly (not passlib)?
import bcrypt
print("3. bcrypt '123456' vs users:", bcrypt.checkpw(b"123456", users_hash.encode()))
print("4. bcrypt '123456' vs admins:", bcrypt.checkpw(b"123456", admins_hash.encode()))

# What if the code used hash_password function reference instead of value?
# The function string representation would be stored
print("5. repr of hash_password:", repr(hash_password))

# Generate fresh hash to confirm it's a different one each time
h1 = pwd.hash("123456")
h2 = pwd.hash("123456")
print("6. Two fresh hashes are different:", h1 != h2)
print("7. Both verify:", pwd.verify("123456", h1) and pwd.verify("123456", h2))

# Try the config PASSWORD variable
from app.core.config import settings
print("8. PASSWORD from config:", getattr(settings, "PASSWORD", "NOT_FOUND"))

# Try loading the init_db module
print("9. The init_db.py uses hash_password (function ref), not password_hash (str)")
print("   See: db.add(User(password=hash_password, ...))")
print("   This stores the function object, which when converted to string")
print("   would be '<function hash_password at 0x...>'")
