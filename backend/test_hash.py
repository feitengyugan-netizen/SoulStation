from passlib.context import CryptContext
import bcrypt

pwd = CryptContext(schemes=['bcrypt'])
h = pwd.hash('123456')
print('New hash:', h)
print('passlib verify:', pwd.verify('123456', h))
print('bcrypt verify:', bcrypt.checkpw(b'123456', h.encode()))

# Try $2b -> $2a
h2a = h.replace('$2b$', '$2a$')
print('bcrypt verify $2a$:', bcrypt.checkpw(b'123456', h2a.encode()))

# Check existing hashes
admins_h = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i'
users_h = '$2b$12$AzF8DWzmXNmKODeXrus77uZVR1QK7fUd35XAN5Z6cYnT6irzwKLFC'
print('\nExisting admins hash:')
print('  passlib verify:', pwd.verify('123456', admins_h))
print('  bcrypt verify:', bcrypt.checkpw(b'123456', admins_h.encode()))
print('Existing users hash:')
print('  passlib verify:', pwd.verify('123456', users_h))
print('  bcrypt verify:', bcrypt.checkpw(b'123456', users_h.encode()))
