"""
scripts/decrypt_backup.py
AES-256-GCM Authenticated Decryption for VeggieVerse Backups.

Usage:
  python scripts/decrypt_backup.py <encrypted_file> [--output <output_file>] [--key <hex_key>] [--key-file <path>] [--verify-only]

Security Principles:
- Validates magic header and verifies AES-256-GCM authentication tag.
- Guarantees zero tampering / corruption detection.
- Gunzips uncompressed payload.
- NEVER logs or outputs secret keys.
"""

import os
import sys
import gzip
import json
import hashlib
import argparse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC_HEADER = b"VVERSE_ENC_V1"
NONCE_LENGTH = 12


def get_decryption_key(key_arg=None, key_file=None):
    """
    Retrieves the 256-bit encryption key from:
    1. CLI arg --key
    2. CLI arg --key-file
    3. Environment variable BACKUP_ENCRYPTION_KEY
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
        print("[ERROR] No decryption key provided.")
        print("Provide via --key, --key-file, or BACKUP_ENCRYPTION_KEY environment variable.")
        sys.exit(1)

    try:
        raw_key = bytes.fromhex(key_hex)
        if len(raw_key) != 32:
            raise ValueError(f"Key length must be 32 bytes (256 bits). Found {len(raw_key)} bytes.")
        return raw_key
    except Exception as e:
        print(f"[ERROR] Invalid decryption key format: {e}")
        sys.exit(1)


def sha256_file(filepath):
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def decrypt_file(input_path, output_path=None, key=None, verify_only=False):
    """
    Decrypts and gunzips an AES-256-GCM encrypted backup file.
    """
    if not os.path.exists(input_path):
        print(f"[ERROR] Encrypted file not found: {input_path}")
        sys.exit(1)

    enc_sha256 = sha256_file(input_path)
    print(f"[INFO] Verifying encrypted file: {input_path}")
    print(f"       Encrypted SHA-256: {enc_sha256}")

    # Check companion metadata file if present
    meta_path = f"{input_path}.meta.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                expected_sha = meta.get("encrypted_sha256")
                if expected_sha and expected_sha != enc_sha256:
                    print(f"[CRITICAL ERROR] SHA-256 mismatch! Metadata: {expected_sha}, Actual: {enc_sha256}")
                    sys.exit(1)
                print("       Metadata SHA-256 match confirmed.")
        except Exception as e:
            print(f"[WARNING] Could not read metadata: {e}")

    # Read binary
    with open(input_path, "rb") as f:
        header = f.read(len(MAGIC_HEADER))
        if header != MAGIC_HEADER:
            print(f"[ERROR] Invalid file header. Expected {MAGIC_HEADER}, got {header}")
            print("File is not a valid VeggieVerse encrypted backup.")
            sys.exit(1)

        nonce = f.read(NONCE_LENGTH)
        if len(nonce) != NONCE_LENGTH:
            print("[ERROR] Corrupted file: truncated nonce.")
            sys.exit(1)

        ciphertext = f.read()

    # Decrypt AES-GCM
    aesgcm = AESGCM(key)
    try:
        compressed_plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=MAGIC_HEADER)
    except Exception as e:
        print("[CRITICAL ERROR] Decryption failed! The key may be incorrect or ciphertext was modified.")
        sys.exit(1)

    # Decompress gzip
    try:
        plaintext = gzip.decompress(compressed_plaintext)
    except Exception as e:
        print(f"[CRITICAL ERROR] Decompression failed: {e}")
        sys.exit(1)

    out_sha256 = hashlib.sha256(plaintext).hexdigest().upper()
    print(f"[SUCCESS] Decryption authenticated. Plaintext size: {len(plaintext):,} bytes")
    print(f"          Decrypted SHA-256: {out_sha256}")

    if verify_only:
        print("[INFO] Verification passed successfully. No output written.")
        return True

    if not output_path:
        # Strip .enc suffix if present
        if input_path.endswith(".enc"):
            output_path = input_path[:-4]
        else:
            output_path = f"{input_path}.dec"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(plaintext)

    print(f"[SUCCESS] Restored plaintext saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="AES-256-GCM file decryption for VeggieVerse backups")
    parser.add_argument("input", help="Path to encrypted .enc file")
    parser.add_argument("--output", "-o", help="Path to output decrypted file")
    parser.add_argument("--key", "-k", help="256-bit encryption key as 64 hex characters")
    parser.add_argument("--key-file", help="Path to file containing hex key")
    parser.add_argument("--verify-only", action="store_true", help="Only verify decryption without saving")
    args = parser.parse_args()

    key = get_decryption_key(args.key, args.key_file)
    decrypt_file(args.input, args.output, key, verify_only=args.verify_only)


if __name__ == "__main__":
    main()
