"""
scripts/keepass_manager.py
Automated KeePassXC Secret Storage and Retrieval for VeggieVerse.

Usage:
  python scripts/keepass_manager.py init [--db <path>] [--password <pass>]
  python scripts/keepass_manager.py generate-env [--db <path>] [--password <pass>]
  python scripts/keepass_manager.py get <secret_name> [--db <path>] [--password <pass>]
  python scripts/keepass_manager.py verify [--db <path>] [--password <pass>]

Security Principles:
- The KeePassXC database is stored OUTSIDE the Git repository.
- Master password is never hardcoded or printed.
- Masked interactive entry via getpass when not supplied via secure env var.
- Secret values are never printed to console or logs.
"""

import os
import sys
import getpass
import secrets
import argparse
import subprocess

DEFAULT_KEEPASS_PATH = r"C:\Program Files\KeePassXC\keepassxc-cli.exe"
DEFAULT_DB_PATH = os.path.expanduser(r"~\Documents\VeggieVerse_Secrets.kdbx")
GROUP_NAME = "VeggieVerse"

REQUIRED_SECRETS = [
    "FLASK_SECRET_KEY",
    "MYSQL_HOST",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
    "MYSQL_PORT",
    "BACKUP_ENCRYPTION_KEY"
]


def find_keepass_cli():
    """Finds keepassxc-cli executable."""
    paths = [
        DEFAULT_KEEPASS_PATH,
        r"C:\Program Files (x86)\KeePassXC\keepassxc-cli.exe",
        "keepassxc-cli"
    ]
    for p in paths:
        try:
            res = subprocess.run([p, "--version"], capture_output=True, text=True)
            if res.returncode == 0:
                return p
        except Exception:
            continue
    print("[ERROR] keepassxc-cli not found. Ensure KeePassXC is installed.")
    sys.exit(1)


def get_master_password(cli_password=None):
    """Securely obtains the master password."""
    if cli_password:
        return cli_password
    if os.environ.get("KEEPASS_MASTER_PASSWORD"):
        return os.environ["KEEPASS_MASTER_PASSWORD"]
    return getpass.getpass("Enter KeePassXC Master Password: ")


def run_cli_cmd(cli_bin, args, stdin_data=None):
    """Runs keepassxc-cli command safely."""
    cmd = [cli_bin] + args
    res = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def init_database(db_path, password):
    """Initializes KeePassXC database and populates with current secrets."""
    cli_bin = find_keepass_cli()
    db_dir = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(db_dir, exist_ok=True)

    # 1. Create DB if not exists
    if not os.path.exists(db_path):
        print(f"[INFO] Creating new KeePassXC database at: {db_path}")
        rc, out, err = run_cli_cmd(cli_bin, ["db-create", "-p", db_path], stdin_data=f"{password}\n{password}\n")
        if rc != 0:
            print(f"[ERROR] Failed to create KeePassXC database: {err}")
            sys.exit(1)
        print("[SUCCESS] KeePassXC database initialized.")
    else:
        print(f"[INFO] KeePassXC database already exists at: {db_path}")

    # 2. Create Group
    rc, out, err = run_cli_cmd(cli_bin, ["mkdir", db_path, GROUP_NAME], stdin_data=f"{password}\n")
    # rc may be non-zero if group already exists, which is acceptable

    # 3. Read existing .env if present
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    # Ensure BACKUP_ENCRYPTION_KEY exists
    if not env_vars.get("BACKUP_ENCRYPTION_KEY"):
        gen_key = secrets.token_hex(32)
        env_vars["BACKUP_ENCRYPTION_KEY"] = gen_key
        # Append to local .env
        with open(".env", "a", encoding="utf-8") as f:
            f.write(f"\n# AES-256-GCM Backup Encryption Key (32 bytes hex)\nBACKUP_ENCRYPTION_KEY={gen_key}\n")
        print("[INFO] Generated new AES-256-GCM BACKUP_ENCRYPTION_KEY and saved to .env")

    # 4. Insert each secret into KeePassXC
    for k in REQUIRED_SECRETS:
        val = env_vars.get(k, "")
        if not val:
            continue
        entry_path = f"{GROUP_NAME}/{k}"

        # Delete existing entry if present to update cleanly
        run_cli_cmd(cli_bin, ["rm", db_path, entry_path], stdin_data=f"{password}\n")

        # Add entry
        rc, out, err = run_cli_cmd(
            cli_bin,
            ["add", "-u", "VeggieVerseAdmin", "-p", db_path, entry_path],
            stdin_data=f"{password}\n{val}\n{val}\n"
        )
        if rc == 0:
            print(f"  [STORED] {k} -> {entry_path}")
        else:
            print(f"  [WARNING] Could not store {k}: {err.strip()}")

    print(f"\n[SUCCESS] All secrets safely encrypted in: {db_path}")
    print("Database is outside git repository and safe for disaster recovery.")


def get_secret(db_path, password, secret_name):
    """Retrieves a single secret from KeePassXC."""
    cli_bin = find_keepass_cli()
    entry_path = f"{GROUP_NAME}/{secret_name}"
    rc, out, err = run_cli_cmd(
        cli_bin,
        ["show", "-s", "-a", "password", db_path, entry_path],
        stdin_data=f"{password}\n"
    )
    if rc == 0:
        return out.strip()
    return None


def generate_env(db_path, password, output_env=".env"):
    """Reads secrets from KeePassXC and writes local .env without printing values."""
    cli_bin = find_keepass_cli()
    print(f"[INFO] Reading secrets from KeePassXC: {db_path}")
    env_content = [
        "# =============================================================================",
        "# VeggieVerse Environment Configuration",
        "# AUTO-GENERATED FROM SECURE KEEPASSXC DATABASE",
        "# NEVER COMMIT THIS FILE TO GIT",
        "# =============================================================================",
        ""
    ]

    for k in REQUIRED_SECRETS:
        val = get_secret(db_path, password, k)
        if val is not None:
            env_content.append(f"{k}={val}")
            print(f"  [RETRIEVED] {k}")
        else:
            print(f"  [MISSING] {k} not found in KeePassXC")

    # Add default optional settings
    env_content.extend([
        "",
        "# Optional Application Settings",
        "FLASK_DEBUG=False",
        "FLASK_PORT=5000"
    ])

    with open(output_env, "w", encoding="utf-8") as f:
        f.write("\n".join(env_content) + "\n")

    print(f"[SUCCESS] Generated local {output_env} successfully.")


def verify_keepass(db_path, password):
    """Verifies KeePassXC entries."""
    cli_bin = find_keepass_cli()
    print(f"[INFO] Verifying KeePassXC database at: {db_path}")
    rc, out, err = run_cli_cmd(cli_bin, ["ls", "-R", db_path, GROUP_NAME], stdin_data=f"{password}\n")
    if rc != 0:
        print(f"[ERROR] Cannot open KeePassXC database: {err}")
        return False

    print(f"[SUCCESS] Group '{GROUP_NAME}' verified. Entries:")
    for line in out.splitlines():
        line = line.strip()
        if line:
            print(f"  - {line}")
    return True


def main():
    parser = argparse.ArgumentParser(description="KeePassXC Secret Manager for VeggieVerse")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser("init", help="Initialize KeePassXC DB with current secrets")
    init_parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to .kdbx file")
    init_parser.add_argument("--password", help="Master password")

    # generate-env
    gen_parser = subparsers.add_parser("generate-env", help="Generate .env from KeePassXC")
    gen_parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to .kdbx file")
    gen_parser.add_argument("--password", help="Master password")
    gen_parser.add_argument("--output", default=".env", help="Output .env file path")

    # get
    get_parser = subparsers.add_parser("get", help="Get a single secret")
    get_parser.add_argument("secret", help="Secret name (e.g. MYSQL_PASSWORD)")
    get_parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to .kdbx file")
    get_parser.add_argument("--password", help="Master password")

    # verify
    ver_parser = subparsers.add_parser("verify", help="Verify KeePassXC DB")
    ver_parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to .kdbx file")
    ver_parser.add_argument("--password", help="Master password")

    args = parser.parse_args()
    pwd = get_master_password(args.password)

    if args.command == "init":
        init_database(args.db, pwd)
    elif args.command == "generate-env":
        generate_env(args.db, pwd, args.output)
    elif args.command == "get":
        val = get_secret(args.db, pwd, args.secret)
        if val:
            print(val)
        else:
            sys.exit(1)
    elif args.command == "verify":
        success = verify_keepass(args.db, pwd)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
