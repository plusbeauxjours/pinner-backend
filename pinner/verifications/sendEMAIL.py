from django.conf import settings
from django.core.mail import send_mail

from django.template.loader import render_to_string


def sendVerificationEMAIL(to, key):
    subject = 'Verify Your Email🔒'
    to = [to, ]
    key = 'https://5d60dc9507a4170008abea29--pinner.netlify.com/verification/{}'.format(key)
    ctx = {'key': key}
    msg_html = render_to_string('account/email_confirm.html', ctx)
    send_mail(subject, msg_html, 'no-reply@pinner.fun', to, html_message=msg_html)
    return "koko"


def sendConfirmEMAIL(to, key):
    subject = 'Verify Your Email🔒'
    to = [to, ]
    key = 'https://5d60dc9507a4170008abea29--pinner.netlify.com/confirm/{}'.format(key)
    ctx = {'key': key}
    msg_html = render_to_string('account/email_confirm.html', ctx)
    send_mail(subject, msg_html, 'no-reply@pinner.fun', to, html_message=msg_html)
    print('223')
    return "koko"