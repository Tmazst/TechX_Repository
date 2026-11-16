"""Issue and validate single-use email codes for TechX customer accounts."""

import hashlib
import hmac
import os
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage

from flask import current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import AccountEmailCode, User, db


CODE_LIFETIME = timedelta(minutes=15)
RESEND_DELAY = timedelta(seconds=60)
MAX_ATTEMPTS = 5
VERIFY_EMAIL = 'verify_email'
RESET_PASSWORD = 'reset_password'


def normalize_email(email):
    return (email or '').strip().lower()


def find_account(email):
    matches = User.query.filter(func.lower(func.trim(User.email)) == normalize_email(email)).limit(2).all()
    return matches[0] if len(matches) == 1 else None


def _digest(value):
    return hmac.new(current_app.secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()


def session_version(user):
    return _digest(f'session:{user.id}:{user.password}')


def _code_digest(user, purpose, code):
    return _digest(f'{purpose}:{user.id}:{normalize_email(user.email)}:{user.password}:{code}')


def _send_email(recipient, purpose, code):
    host = os.environ['AUTH_SMTP_HOST']
    sender = os.environ['AUTH_SMTP_FROM']
    username = os.environ.get('AUTH_SMTP_USERNAME')
    password = os.environ.get('AUTH_SMTP_PASSWORD')
    use_ssl = os.environ.get('AUTH_SMTP_SSL', '0') == '1'
    port = int(os.environ.get('AUTH_SMTP_PORT', '465' if use_ssl else '587'))

    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = 'Verify your TechX email' if purpose == VERIFY_EMAIL else 'Reset your TechX password'
    message.set_content(
        f'Your TechX code is {code}. It expires in 15 minutes and can be used once. '
        'If you did not request this code, you can ignore this email.'
    )

    tls = ssl.create_default_context()
    connection = (
        smtplib.SMTP_SSL(host, port, timeout=10, context=tls)
        if use_ssl else smtplib.SMTP(host, port, timeout=10)
    )
    with connection as smtp:
        if not use_ssl:
            smtp.starttls(context=tls)
        if username:
            smtp.login(username, password or '')
        smtp.send_message(message)


def issue_code(user, purpose):
    now = datetime.utcnow()
    code = f'{secrets.randbelow(100_000_000):08d}'
    digest = _code_digest(user, purpose, code)
    values = {
        'digest': digest,
        'issued_at': now,
        'expires_at': now + CODE_LIFETIME,
        'attempts': 0,
        'consumed': False,
    }

    challenge = AccountEmailCode.query.filter_by(user_id=user.id, purpose=purpose)
    updated = challenge.filter(AccountEmailCode.issued_at <= now - RESEND_DELAY).update(
        values, synchronize_session=False
    )
    if not updated and challenge.first() is not None:
        db.session.rollback()
        return False

    if not updated:
        db.session.add(AccountEmailCode(user_id=user.id, purpose=purpose, **values))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False

    try:
        _send_email(user.email, purpose, code)
    except (KeyError, ValueError, OSError, smtplib.SMTPException) as error:
        current_app.logger.error('TechX account email delivery failed (%s)', type(error).__name__)
        return False
    return True


def consume_code(user, purpose, code):
    """Reserve a valid code in the caller's transaction, or record a failed guess."""
    if user is None:
        return False

    candidates = AccountEmailCode.query.filter_by(user_id=user.id, purpose=purpose, consumed=False).filter(
        AccountEmailCode.expires_at > datetime.utcnow(),
        AccountEmailCode.attempts < MAX_ATTEMPTS,
    )
    matched = candidates.filter_by(digest=_code_digest(user, purpose, code)).update(
        {'consumed': True}, synchronize_session=False
    )
    if matched:
        return True

    candidates.update({'attempts': AccountEmailCode.attempts + 1}, synchronize_session=False)
    db.session.commit()
    return False
