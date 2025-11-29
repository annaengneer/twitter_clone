from django.core.mail import send_mail
from django.conf import settings

def send_notification_email(to_user, from_user, notification_type, extra_text=None):
    subject = '新しい通知があります'
    if notification_type == 'like':
        message = f'{from_user.display_name}さんがあなたの投稿にいいねしました。'
    elif notification_type == 'follow':
        message = f'{from_user.display_name}さんがあなたをフォローしました。'
    elif notification_type == 'comment':
        message = f"{from_user.display_name}さんがコメントしました:\n\n{extra_text or ''}"
    else:
        message = '新しい通知があります。'

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_user.email]
    )