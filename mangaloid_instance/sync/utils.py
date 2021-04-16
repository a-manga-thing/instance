from json import dumps
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64encode, b64decode
from asyncio import get_event_loop
from concurrent.futures.process import ProcessPoolExecutor


async def _run_async(call, *args):
    with ProcessPoolExecutor() as pool:
        return await get_event_loop().run_in_executor(pool, call, *args)

def _get_key_pair():
    private = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend())
    public = private.public_key()
    private_string = private.private_bytes(encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()).decode("utf-8")
    public_string = public.public_bytes(encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo).decode("utf-8")
    return private_string, public_string

def _create_sync_payload(dc, key):
    string = dumps(dc).encode("utf-8")
    pkey = serialization.load_pem_public_key(key.encode("utf-8"), backend=default_backend())
    return b64encode(pkey.encrypt(string, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))).decode("ascii")

def _get_sync_payload(b64, key):
    byte = b64decode(b64)
    pkey = serialization.load_pem_private_key(key.encode("utf-8"), None ,backend=default_backend())
    return loads(pkey.decrypt(byte, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )).decode("utf-8"))

async def get_key_pair():
    """Creates a public/private key pair and returns them in PEM format as strings"""
    return await _run_async(_get_key_pair)

async def create_sync_payload(dc, key):
    """Converts dictionary to JSON, encrypts it with provided public key (PEM)
    and returns it as a Base64-encoded string.
    """
    return await _run_async(_create_sync_payload, dc, key)

async def get_sync_payload(b64, key):
    """Converts Base64-encoded string created with 'create_sync_payload' to dictionary"""
    return await _run_async(_get_sync_payload, b64, key)