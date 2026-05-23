from django.conf import settings
import requests

def send_notification_email(to_user, from_user, notification_type, extra_text=None):
    mailgun_domain = getattr(settings, "MAILGUN_DOMAIN", None)
    mailgun_api_key = getattr(settings, "MAILGUN_API_KEY", None)
    if not mailgun_domain or not mailgun_api_key:
        return None

    subject = '新しい通知があります'
    if notification_type == 'like':
        text = f'{from_user.display_name}さんがあなたの投稿にいいねしました。'
    elif notification_type == 'follow':
        text = f'{from_user.display_name}さんがあなたをフォローしました。'
    elif notification_type == 'comment':
        text = f"{from_user.display_name}さんがコメントしました:\n\n{extra_text or ''}"
    else:
        text = '新しい通知があります。'

    try:
        return requests.post(
            f'https://api.mailgun.net/v3/{mailgun_domain}/messages',
            auth=('api', mailgun_api_key),
            data={
                'from': f'通知 <mailgun@{mailgun_domain}>',
                'to': [to_user.email],
                'subject': subject,
                'text': text,
            },
            timeout=5,
        )
    except requests.RequestException:
        return None
