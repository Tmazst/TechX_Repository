"""Restricted Cloudflare DNS operations for customer-owned eswtn.com namespaces."""

import ipaddress
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CLOUDFLARE_API_BASE = 'https://api.cloudflare.com/client/v4'
ALLOWED_RECORD_TYPES = ('A', 'AAAA', 'CNAME', 'MX', 'TXT')
PROXY_RECORD_TYPES = ('A', 'AAAA', 'CNAME')
DNS_LABEL_PATTERN = re.compile(r'^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$')


class DnsServiceError(RuntimeError):
    """Raised when the DNS provider cannot complete an operation."""


class DnsValidationError(ValueError):
    """Raised when a customer DNS record is unsafe or malformed."""


def cloudflare_configured():
    return bool(
        os.environ.get('CLOUDFLARE_API_TOKEN')
        and os.environ.get('CLOUDFLARE_ZONE_ID')
    )


def cloudflare_zone_id():
    return os.environ.get('CLOUDFLARE_ZONE_ID', '').strip()


def _cloudflare_request(method, path, payload=None, query=None):
    token = os.environ.get('CLOUDFLARE_API_TOKEN', '').strip()
    zone_id = cloudflare_zone_id()
    if not token or not zone_id:
        raise DnsServiceError('Cloudflare DNS automation is not configured on the server.')

    url = f'{CLOUDFLARE_API_BASE}{path}'
    if query:
        url = f'{url}?{urlencode(query)}'

    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    request_object = Request(
        url,
        data=body,
        method=method,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'TechX-eswtn-DNS/1.0'
        }
    )

    try:
        with urlopen(request_object, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        message = f'Cloudflare rejected the DNS request ({error.code}).'
        try:
            error_payload = json.loads(error.read().decode('utf-8'))
            provider_errors = error_payload.get('errors') or []
            if provider_errors and provider_errors[0].get('message'):
                message = provider_errors[0]['message']
        except (ValueError, UnicodeDecodeError, AttributeError):
            pass
        raise DnsServiceError(message) from error
    except (URLError, TimeoutError, OSError) as error:
        raise DnsServiceError('Cloudflare could not be reached. Please try again shortly.') from error

    if not result.get('success'):
        errors = result.get('errors') or []
        message = errors[0].get('message') if errors else 'Cloudflare could not complete the DNS request.'
        raise DnsServiceError(message)

    return result.get('result')


def _valid_hostname(value):
    hostname = (value or '').strip().lower().rstrip('.')
    if not hostname or len(hostname) > 253:
        return False
    return all(DNS_LABEL_PATTERN.fullmatch(label) for label in hostname.split('.'))


def normalize_record_name(raw_name, namespace):
    namespace = (namespace or '').strip().lower().rstrip('.')
    name = (raw_name or '').strip().lower().rstrip('.')

    if not _valid_hostname(namespace):
        raise DnsValidationError('The assigned namespace is invalid.')

    base_domain = '.'.join(namespace.split('.')[-2:])

    if name in ('', '@'):
        normalized = namespace
    elif name == namespace or name.endswith(f'.{namespace}'):
        normalized = name
    elif name == base_domain or name.endswith(f'.{base_domain}'):
        raise DnsValidationError('This record is outside your assigned namespace.')
    else:
        normalized = f'{name}.{namespace}'

    if normalized != namespace and not normalized.endswith(f'.{namespace}'):
        raise DnsValidationError('This record is outside your assigned namespace.')
    if not _valid_hostname(normalized):
        raise DnsValidationError('Use valid DNS labels separated by dots.')

    return normalized


def normalize_record_content(record_type, raw_content):
    record_type = (record_type or '').upper()
    content = (raw_content or '').strip()

    if record_type not in ALLOWED_RECORD_TYPES:
        raise DnsValidationError('This DNS record type is not supported.')

    if record_type in ('A', 'AAAA'):
        try:
            address = ipaddress.ip_address(content)
        except ValueError as error:
            raise DnsValidationError(f'Enter a valid {record_type} address.') from error
        expected_version = 4 if record_type == 'A' else 6
        if address.version != expected_version:
            raise DnsValidationError(f'Enter a valid IPv{expected_version} address.')
        return str(address)

    if record_type in ('CNAME', 'MX'):
        hostname = content.lower().rstrip('.')
        if not _valid_hostname(hostname):
            raise DnsValidationError('Enter a valid destination hostname, without http:// or https://.')
        return hostname

    if not content or len(content) > 2048:
        raise DnsValidationError('TXT content must contain between 1 and 2048 characters.')
    return content


def build_record_payload(record_type, name, content, ttl, proxied, priority, namespace):
    record_type = (record_type or '').upper()
    normalized_name = normalize_record_name(name, namespace)
    normalized_content = normalize_record_content(record_type, content)

    try:
        ttl = int(ttl)
    except (TypeError, ValueError) as error:
        raise DnsValidationError('Select a valid TTL.') from error
    if ttl != 1 and not 60 <= ttl <= 86400:
        raise DnsValidationError('TTL must be Automatic or between 60 and 86400 seconds.')

    payload = {
        'type': record_type,
        'name': normalized_name,
        'content': normalized_content,
        'ttl': ttl,
        'proxied': bool(proxied) if record_type in PROXY_RECORD_TYPES else False
    }

    if record_type == 'MX':
        try:
            priority_value = 10 if priority in (None, '') else int(priority)
        except (TypeError, ValueError) as error:
            raise DnsValidationError('MX priority must be a number from 0 to 65535.') from error
        if not 0 <= priority_value <= 65535:
            raise DnsValidationError('MX priority must be a number from 0 to 65535.')
        payload['priority'] = priority_value

    return payload


def cloudflare_find_records(name):
    zone_id = cloudflare_zone_id()
    return _cloudflare_request(
        'GET',
        f'/zones/{zone_id}/dns_records',
        query={'name': name, 'per_page': 100}
    ) or []


def cloudflare_create_record(payload):
    zone_id = cloudflare_zone_id()
    return _cloudflare_request('POST', f'/zones/{zone_id}/dns_records', payload=payload)


def cloudflare_update_record(record_id, payload):
    zone_id = cloudflare_zone_id()
    return _cloudflare_request(
        'PATCH',
        f'/zones/{zone_id}/dns_records/{record_id}',
        payload=payload
    )


def cloudflare_delete_record(record_id):
    zone_id = cloudflare_zone_id()
    return _cloudflare_request('DELETE', f'/zones/{zone_id}/dns_records/{record_id}')
