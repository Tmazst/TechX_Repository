# TechX customer email authentication

Set these values in the environment of the Gunicorn service before deploying:

| Variable | Value |
| --- | --- |
| `TECHX_SECRET_KEY` | A new random secret, shared by all workers. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `AUTH_SMTP_HOST` | SMTP submission hostname. |
| `AUTH_SMTP_PORT` | Usually `587` for STARTTLS or `465` for implicit TLS. |
| `AUTH_SMTP_SSL` | `1` for implicit TLS or `0` for STARTTLS. |
| `AUTH_SMTP_FROM` | Sender address authorized by the SMTP provider. |
| `AUTH_SMTP_USERNAME` and `AUTH_SMTP_PASSWORD` | SMTP credentials when required. |

Keep HTTPS enabled. Session cookies require HTTPS by default. Set `TECHX_SECURE_COOKIES=0` only when testing locally over HTTP.

Back up the database before deploying. The app creates the `account_email_code` table during the account flow. The new secret signs out existing sessions. When existing customers sign in again, accounts with an unverified email receive a verification code. Any legacy accounts that share an email after case and whitespace normalization require admin reconciliation before sign-in.

DNS access follows the domain's linked user ID. A verified customer visiting My Domains can claim an unlinked request or approved domain associated with their verified email. Review any existing domain links that use a different owner email before launch. Domain administrators still need a verified TechX account using an address listed in `DOMAIN_ADMIN_EMAILS`.

On staging, use two separate mailboxes to verify delivery and sign-in. Approve a test domain for each account and confirm both customers see their assigned domains. Reset a password from a separate browser and confirm the old sessions require sign-in again. Use a staging database and SMTP configuration before changing the live service.
