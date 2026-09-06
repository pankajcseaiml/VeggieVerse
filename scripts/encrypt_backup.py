"""
scripts/encrypt_backup.py
AES-256-GCM Authenticated Encryption for VeggieVerse Backups.

Usage:
  python scripts/encrypt_backup.py <input_file> [--output <output_file>] [--key <hex_key>] [--key-file <path>]

Security Principles:
- AES-256-GCM authenticated encryption (confidentiality + integrity).
- Gzip compression prior to encryption.
- Computes SHA-256 checksum of the resulting encrypted file.
- NEVER logs or outputs secret keys.
"""

import os
import sys
import gzip
import json
import hashlib
import argparse
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC_HEADER = b"VVERSE_ENC_V1"
NONCE_LENGTH = 12  # 96 bits for GCM


def get_encryption_key(key_arg=None, key_file=None):
    """
    Retrieves the 256-bit encryption key from:
    1. CLI arg --key
    2. CLI arg --key-file
    3. Environment variable BACKUP_ENCRYPTION_KEY
    Returns 32 raw bytes.
    """
    key_hex = None
    if key_arg:
        key_hex = key_arg.strip()
    elif key_file and os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            key_hex = f.read().strip()
    elif os.environ.get("BACKUP_ENCRYPTION_KEY"):
        key_hex = os.environ["BACKUP_ENCRYPTION_KEY"].strip()

    if not key_hex:
        print("[ERROR] No encryption key provided.")
        print("Provide via --key, --key-file, or BACKUP_ENCRYPTION_KEY environment variable.")
        print("To generate a new key: python -c \"import secrets; print(secrets.token_hex(32))\"")
        sys.exit(1)

    try:
        raw_key = bytes.fromhex(key_hex)
        if len(raw_key) != 32:
            raise ValueError(f"Key length must be 32 bytes (256 bits). Found {len(raw_key)} bytes.")
        return raw_key
    except Exception as e:
        print(f"[ERROR] Invalid encryption key format: {e}")
        sys.exit(1)


def sha256_file(filepath):
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def encrypt_file(input_path, output_path=None, key=None):
    """
    Compresses with gzip and encrypts using AES-256-GCM.
    Writes output file and accompanying metadata JSON.
    """
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    if not output_path:
        output_path = f"{input_path}.enc"

    # 1. Read input data
    with open(input_path, "rb") as f:
        plaintext = f.read()

    orig_size = len(plaintext)
    orig_sha256 = hashlib.sha256(plaintext).hexdigest().upper()

    # 2. Compress with gzip
    compressed = gzip.compress(plaintext, compresslevel=9)
    comp_size = len(compressed)

    # 3. Encrypt with AES-GCM
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_LENGTH)
    ciphertext = aesgcm.encrypt(nonce, compressed, associated_data=MAGIC_HEADER)

    # 4. Write encrypted payload: MAGIC_HEADER (13 bytes) + NONCE (12 bytes) + CIPHERTEXT
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(MAGIC_HEADER)
        f.write(nonce)
        f.write(ciphertext)

    enc_size = os.path.getsize(output_path)
    enc_sha256 = sha256_file(output_path)

    # 5. Metadata manifest (no keys stored!)
    meta_path = f"{output_path}.meta.json"
    metadata = {
        "format": "VeggieVerse_AES256GCM",
        "version": "1.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "original_file": os.path.basename(input_path),
        "original_size_bytes": orig_size,
        "original_sha256": orig_sha256,
        "compressed_size_bytes": comp_size,
        "encrypted_size_bytes": enc_size,
        "encrypted_sha256": enc_sha256,
        "cipher": "AES-256-GCM",
        "compression": "gzip-9"
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[SUCCESS] Encrypted: {output_path}")
    print(f"  Original size:  {orig_size:,} bytes")
    print(f"  Encrypted size: {enc_size:,} bytes")
    print(f"  SHA-256:        {enc_sha256}")
    print(f"  Metadata:       {meta_path}")
    return output_path, enc_sha256


def main():
    parser = argparse.ArgumentParser(description="AES-256-GCM file encryption for VeggieVerse backups")
    parser.add_argument("input", help="Path to input file to encrypt")
    parser.add_argument("--output", "-o", help="Path to output .enc file")
    parser.add_argument("--key", "-k", help="256-bit encryption key as 64 hex characters")
    parser.add_argument("--key-file", help="Path to file containing hex key")
    args = parser.parse_args()

    key = get_encryption_key(args.key, args.key_file)
    encrypt_file(args.input, args.output, key)


if __name__ == "__main__":
    main()
