from django.conf import settings
from django.core.mail import send_mail

from django.template.loader import render_to_string


def sendVerificationEMAIL(to, key):
    subject = 'Verify Your Email🔒'
    to = [to, ]
    key = 'https://www.pinner.fun/verification/{}'.format(key)
    ctx = {'key': key}
    msg_html = render_to_string('account/email_confirm.html', ctx)
    send_mail(subject, strip_tags(msg_html), 'no-reply@pinner.fun', to, html_message=msg_html)
    return


def sendConfirmEMAIL(to, key):
    subject = 'Verify Your Email🔒'
    to = [to, ]
    key = 'https://www.pinner.fun/confirm/{}'.format(key)
    ctx = {'key': key}
    msg_html = render_to_string('account/email_confirm.html', ctx)
    send_mail(subject, strip_tags(msg_html), 'no-reply@pinner.fun', to, html_message=msg_html)
    return
