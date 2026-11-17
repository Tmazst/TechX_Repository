"""DNS checks for the manually provisioned business email pilot."""

import re

import dns.exception
import dns.resolver


LABEL = re.compile(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?')
MAIL_HOST = 'mail.eswtn.com'
MAIL_SPF = 'ip4:159.198.68.129'


def normalize_domain(value):
    try:
        domain = value.strip().rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError as error:
        raise ValueError('Enter a domain such as company.com.') from error
    labels = domain.split('.')
    if (len(domain) > 253 or len(labels) < 2 or labels[-1].isdigit()
            or not all(LABEL.fullmatch(label) for label in labels)):
        raise ValueError('Enter a domain such as company.com.')
    return domain


def lookup_records(name, record_type):
    try:
        return list(dns.resolver.resolve(f'{name}.', record_type, lifetime=3, search=False))
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []
    except dns.exception.DNSException:
        return None


def has_verification_record(item):
    answers = lookup_records(item.verification_name, 'TXT')
    if answers is None:
        return None
    return any(b''.join(answer.strings) == item.verification_code.encode('ascii') for answer in answers)


def mail_dns_hosts(domain):
    answers = lookup_records(domain, 'MX')
    if answers is None:
        return None
    return [str(answer.exchange).lower().rstrip('.') for answer in answers]


def mail_dns_status(domain):
    # A previous provider still listed in MX can continue to receive mail.
    hosts = mail_dns_hosts(domain)
    return bool(hosts) and all(host == MAIL_HOST for host in hosts)
