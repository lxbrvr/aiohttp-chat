import typing as t
import binascii
import hashlib
import os
from datetime import datetime, timedelta
from importlib import import_module

import jwt


def generate_jwt(exp_in_secs: int, secret_key: str, payload: dict = None) -> str:
    exp = datetime.utcnow() + timedelta(seconds=exp_in_secs)
    payload = payload or {}
    payload.update({'exp': exp})
    token = jwt.encode(payload=payload, key=secret_key)
    return token.decode('utf-8')


def import_string(path: str) -> t.Any:
    """
    Helps to import string defined like "path.to.Class".
    """

    try:
        module_path, class_name = path.rsplit('.', 1)
    except ValueError as e:
        raise ImportError(f"{path} doesn't look like a module path.") from e

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f'Module "{module_path}" does not define '
            f'a "{class_name}" attribute/class'
        ) from e


def hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(30)).hexdigest().encode('ascii')

    password_hash = hashlib.pbkdf2_hmac(
        hash_name='sha512',
        password=password.encode('utf-8'),
        salt=salt,
        iterations=10000,
    )

    return (salt + binascii.hexlify(password_hash)).decode('ascii')


def verify_password(raw_password: str, real_password: str) -> bool:
    salt = real_password[:64]
    password = real_password[64:]
    password_hash = hashlib.pbkdf2_hmac(
        hash_name='sha512',
        password=raw_password.encode('utf-8'),
        salt=salt.encode('ascii'),
        iterations=10000,
    )

    return binascii.hexlify(password_hash).decode('ascii') == password