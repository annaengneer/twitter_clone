from django.conf import settings
import requests

def send_notification_email(to_user, from_user, notification_type, extra_text=None):
    subject = '新しい通知があります'
    if notification_type == 'like':
        text = f'{from_user.display_name}さんがあなたの投稿にいいねしました。'
    elif notification_type == 'follow':
        text = f'{from_user.display_name}さんがあなたをフォローしました。'
    elif notification_type == 'comment':
        text = f"{from_user.display_name}さんがコメントしました:\n\n{extra_text or ''}"
    else:
        text = '新しい通知があります。'

    return requests.post(
        f'https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages',
        auth=('api', settings.MAILGUN_API_KEY),
        data={
            'from': f'通知 <mailgun@{settings.MAILGUN_DOMAIN}>',
            'to': [to_user.email],
            'subject': subject,
            'text': text,
        }
    )