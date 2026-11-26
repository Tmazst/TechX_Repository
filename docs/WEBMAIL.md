# TechX Webmail deployment

The TechX website serves `/webmail`. Roundcube serves the inbox and mailbox sign-in at `https://webmail.eswtn.com/`. It reads mail from Dovecot at `mail.eswtn.com:993` over TLS and submits through Postfix at `mail.eswtn.com:587` with STARTTLS and mailbox authentication. The mailbox password is entered on the Roundcube sign-in page.

## Check the mail server

On the VPS, check listeners and verify the certificates for both mail services. These checks use the same hostname and TLS modes as Roundcube.

```bash
sudo ss -ltn '( sport = :993 or sport = :587 or sport = :8097 )'
openssl s_client -connect mail.eswtn.com:993 -servername mail.eswtn.com -verify_hostname mail.eswtn.com -verify_return_error -brief </dev/null
openssl s_client -starttls smtp -connect mail.eswtn.com:587 -servername mail.eswtn.com -verify_hostname mail.eswtn.com -verify_return_error -brief </dev/null
```

Verify that Dovecot and Postfix accept the full provisioned mailbox address for authentication. Use a pilot mailbox with `sudo doveadm auth test pilot@company.eswtn.com` and enter its password at the prompt. Legacy local accounts may use short usernames. With multiple hosted domains, two mailboxes such as `info@first.example` and `info@second.example` need separate logins and storage. Confirm that submission applies sender ownership checks for each authenticated mailbox, including any aliases TechX provisions.

## Start Roundcube

This configuration uses Docker Engine with Compose v2. Run these commands from the checked-out TechX repository on the VPS, prefixing Docker with `sudo` if your account requires it. Check that port `8097` is free before starting.

```bash
cd deploy/webmail
docker compose config --quiet
docker compose build --pull roundcube
docker compose up -d --no-build roundcube
docker compose ps
curl --fail --silent --show-error -H 'Host: webmail.eswtn.com' http://127.0.0.1:8097/ -o /dev/null
```

The published container port is local to Nginx. The `roundcube-db` volume holds Roundcube settings and address books. The `roundcube-app` volume holds the generated application configuration, including the session encryption key. Include both volumes in the VPS backups. Mail stays on Dovecot. Update the base image tag in `deploy/webmail/Dockerfile` when upgrading Roundcube. Review the [upstream security releases](https://roundcube.net/news/security/) and back up the volumes before an upgrade.

## Enable HTTPS

Add a DNS-only `A` record for `webmail.eswtn.com` pointing to the VPS that runs Nginx. First check for an existing vhost or certificate for this name. The sample uses IPv4, so publish an `AAAA` record only if the VPS also serves this vhost on IPv6.

If the hostname needs a new certificate, create `/var/www/letsencrypt` and enable this temporary Nginx site in `sites-available/webmail.eswtn.com` with a symlink in `sites-enabled`.

```nginx
server {
    listen 80;
    server_name webmail.eswtn.com;
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
        try_files $uri =404;
    }
    location / { return 404; }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
sudo certbot certonly --webroot -w /var/www/letsencrypt --cert-name webmail.eswtn.com -d webmail.eswtn.com
```

From `deploy/webmail`, install the final vhost and make sure the `sites-enabled` symlink points to it. If Certbot reports different paths for an existing certificate, update the sample before installing it.

```bash
sudo install -m 0644 webmail.nginx.conf /etc/nginx/sites-available/webmail.eswtn.com
sudo nginx -t && sudo systemctl reload nginx
curl --fail --silent --show-error https://webmail.eswtn.com/ -o /dev/null
```

Confirm that Certbot has automatic renewal enabled and a deploy hook that reloads Nginx after renewal. Check renewal with `sudo certbot renew --cert-name webmail.eswtn.com --dry-run`.

## Verify and publish

Sign in at `https://webmail.eswtn.com/` with a pilot mailbox. Send and receive an external test message, reply with an attachment, and sign out. Repeat with another mailbox and confirm each login shows its own inbox and sends from its own address. For a multi-domain rollout, include two pilot addresses with the same local part on different domains.

After the pilot succeeds, deploy this website revision and set `TECHX_WEBMAIL_ENABLED=1` in the environment for `techx.service`. Restart `techx.service` and verify `/webmail`, the guest navigation, Business Email, and the Webmail button on a ready mailbox in My Email. To hide the website entry, unset `TECHX_WEBMAIL_ENABLED` and restart the service. To take the inbox endpoint offline, stop the Roundcube service and disable its Nginx vhost.

## Install Webmail on your device

The Roundcube image includes the TechX Webmail PWA. Its launch URL is `https://webmail.eswtn.com/`, so the installed icon opens the inbox or the mailbox sign-in screen if the session has expired. Installation uses the browser's app menu. Supported browsers may also show an Install Webmail button on the sign-in screen. The app uses the live mailbox over HTTPS and requires an internet connection.

For an existing deployment, rebuild and recreate the Roundcube container with the commands in [Start Roundcube](#start-roundcube). Keep the existing Compose project and both named volumes. Verify Webmail before restarting `techx.service` to publish the updated website instructions.

```bash
curl -fsS https://webmail.eswtn.com/ | grep -F 'rel="manifest"'
curl -fsS https://webmail.eswtn.com/static.php/plugins/techx_pwa/manifest.json
```

Install from the Webmail hostname on a desktop browser and a phone. Launch from the installed icon, verify that it opens Webmail directly, and test sign-in, inbox access and sending. The [website's Webmail page](https://techx.eswtn.com/webmail) lists the installation steps by device.
