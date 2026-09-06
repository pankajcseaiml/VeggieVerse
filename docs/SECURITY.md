# Security Architecture — VeggieVerse

## Secret Management

This project uses a strict separation between code and secrets.

### Principles

1. **GitHub is NOT the secret store.** Even though the repository is private, real secrets are never committed.
2. **All secrets live in `.env`** — a file that is git-ignored and exists only on the developer's machine.
3. **`.env.example`** contains only variable names with empty placeholders — it is safe to commit.
4. **Startup validation** — the application exits immediately with a clear error if any required secret is missing.

### Secret Storage Architecture

```
Password Manager (Bitwarden / KeePass / 1Password)
    │
    │  (manual copy by developer)
    ▼
.env  (local machine only — git-ignored)
    │
    │  (loaded at startup by python-dotenv)
    ▼
Application (Flask / db.py)
```

### Secrets Managed by This Project

| Variable | Purpose | Rotation Recommended |
|---|---|---|
| `FLASK_SECRET_KEY` | Flask session signing key | On any suspected compromise |
| `MYSQL_PASSWORD` | MySQL database access | On any suspected compromise |

**Values are never printed, logged, or exposed anywhere in this documentation.**

---

## Security Incident — Pre-Migration Findings

During the initial migration audit (September 2026), the following issues were identified and remediated:

### Issues Found

| Issue | Severity | Status |
|---|---|---|
| MySQL password hardcoded in `db.py` | 🔴 Critical | **REMEDIATED** |
| Flask secret key hardcoded in `app.py` | 🔴 Critical | **REMEDIATED** |
| Both secrets committed in all 3 git commits | 🔴 Critical | **REMEDIATED — history rewritten** |
| No `.gitignore` existed | 🟡 High | **REMEDIATED** |
| `__pycache__/` committed | 🟢 Low | **REMEDIATED** |

### Remediation Actions Taken

1. **Git history rewritten** using `git-filter-repo --replace-text` to purge the literal secret values from all commits
2. **`db.py` refactored** — all MySQL credentials now loaded from environment variables via `python-dotenv`
3. **`app.py` refactored** — `FLASK_SECRET_KEY` now loaded from environment variable
4. **Startup validation added** — both files call a validation function on import that exits with a descriptive error if required env vars are missing
5. **`.gitignore` created** — protects `.env`, `venv/`, `__pycache__/`, logs, keys, and backups
6. **`.env.example` created** — documents required variable names with no values

### Action Required

> ⚠️ **Because the secrets were previously on GitHub (even in a private repository), treat them as potentially compromised.**
>
> **Recommended action:** Rotate both secrets after completing the migration:
> - Generate a new `FLASK_SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
> - Change your MySQL root password: `ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_strong_password';`
>
> Update your `.env` and password manager with the new values.

---

## `.gitignore` Protection

The following patterns are protected from accidental commits:

```
.env          # Real environment file
.env.*        # Any variant (e.g. .env.production)
*.pem         # TLS/SSL private keys
*.key         # Private keys
*.p12         # Certificate bundles
credentials.* # Any credentials file
secrets.*     # Any secrets file
venv/         # Virtual environment
__pycache__/  # Python bytecode
*.log         # Log files
```

`.env.example` is explicitly **excluded** from the ignore pattern so it can be committed safely.

---

## GitHub Security Recommendations

The following GitHub repository settings are recommended:

- [ ] **Repository visibility: Private** ← Verify this is set
- [ ] **Enable Secret Scanning** (Settings → Security → Code security)
- [ ] **Enable Push Protection** (prevents accidental secret pushes)
- [ ] **Enable Dependabot alerts** (Settings → Security → Dependabot)
- [ ] **Enable 2FA** on your GitHub account
- [ ] **Review repository collaborators** — principle of least privilege

---

## Reporting Security Issues

If you discover a security issue in this project, do not open a public GitHub issue.  
Contact the repository owner directly.
