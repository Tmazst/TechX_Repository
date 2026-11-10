# eswtn.com DNS Management — Phase 2

## Architecture

- Sav remains the registrar for `eswtn.com`.
- Cloudflare remains the authoritative DNS provider.
- TechX customers never receive Cloudflare credentials.
- Each approved customer receives one assigned namespace such as `company.eswtn.com`.
- The TechX backend validates ownership before every Cloudflare operation.
- Email mailbox provisioning remains separate from DNS management.

## Required server environment

```env
CLOUDFLARE_ZONE_ID=your_cloudflare_zone_id
CLOUDFLARE_API_TOKEN=your_scoped_api_token
DOMAIN_ADMIN_EMAILS=thabo@example.com,support@techxolutions.com
```

Create a dedicated Cloudflare API token with:

- Permission: Zone → DNS → Edit
- Zone resource: Include → Specific zone → eswtn.com
- Optional security: restrict the token to the production server IP
- Never use or store the Global API Key

Restart the application after setting the variables.

## Administration

1. Sign in using an email listed in `DOMAIN_ADMIN_EMAILS`.
2. Open `/domain-admin`.
3. Review pending namespace requests.
4. Approve only after verifying the customer and intended use.
5. Approval creates an active `DomainAccount` and unlocks the customer's DNS workspace.

Approval is blocked if:

- Cloudflare credentials are missing.
- The request has already been reviewed.
- A local account already owns the namespace.
- Cloudflare already contains records at the exact requested hostname.

## Customer DNS controls

Customers may create, edit and delete only:

- A
- AAAA
- CNAME
- MX
- TXT

The backend enforces:

- The record name must equal the assigned namespace or be a child of it.
- A customer cannot edit `eswtn.com`, `techx.eswtn.com` or another customer's namespace.
- Proxying is available only for A, AAAA and CNAME records.
- MX priority must be between 0 and 65535.
- TTL must be Automatic or between 60 and 86400 seconds.
- Each account starts with a 25-record limit.
- All record changes are recorded in `DnsAuditLog`.

## New database tables

Tables are created with `checkfirst=True` when a domain route is first accessed:

- `domain_account`
- `managed_dns_record`
- `dns_audit_log`

Existing `domain_request` records remain unchanged.

## Operational notes

- Records created manually in Cloudflare are not imported automatically.
- Customer dashboards show records created through TechX.
- If a managed record is changed or deleted directly in Cloudflare, reconcile it manually before the customer edits it again.
- Back up the application database before deployment and before any future schema migration.
