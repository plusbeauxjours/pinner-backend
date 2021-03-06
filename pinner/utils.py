import hashlib
from functools import partial
from slacker import Slacker
from django.conf import settings


def hash_file(file, block_size=65536):
    hasher = hashlib.md5()
    for buf in iter(partial(file.read, block_size), b''):
        hasher.update(buf)

    return hasher.hexdigest()


def notify_slack(channel,  attachments):
    if not settings.SLACK_TOKEN:
        return False
    try:
        slack = Slacker(settings.SLACK_TOKEN)
        slack.chat.post_message(channel, attachments=attachments)
    except:
        return False
    return True
