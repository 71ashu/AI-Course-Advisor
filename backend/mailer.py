"""SMTP helpers for transactional email (password reset)."""
import smtplib
from email.message import EmailMessage


def is_email_configured(config) -> bool:
    return bool(config.get('MAIL_SERVER'))


def send_password_reset_email(config, to_email: str, reset_url: str) -> None:
    """Send a password reset link via SMTP. Raises on failure."""
    sender = config.get('MAIL_DEFAULT_SENDER') or config.get('MAIL_USERNAME')
    if not sender:
        raise ValueError('MAIL_DEFAULT_SENDER or MAIL_USERNAME is required to send mail')

    hours = config.get('PASSWORD_RESET_TOKEN_HOURS', 1)
    msg = EmailMessage()
    msg['Subject'] = 'Reset your AI Course Advisor password'
    msg['From'] = sender
    msg['To'] = to_email
    msg.set_content(
        f'You requested a password reset.\n\n'
        f'Open this link (expires in {hours} hour(s)):\n{reset_url}\n\n'
        f'If you did not request this, you can ignore this email.'
    )

    server = config['MAIL_SERVER']
    port = int(config.get('MAIL_PORT') or 587)
    use_tls = config.get('MAIL_USE_TLS', True)

    with smtplib.SMTP(server, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        user = config.get('MAIL_USERNAME')
        password = config.get('MAIL_PASSWORD')
        if user and password is not None:
            smtp.login(user, password)
        smtp.send_message(msg)
