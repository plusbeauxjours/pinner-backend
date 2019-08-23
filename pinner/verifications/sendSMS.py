from django.conf import settings
from twilio.rest import Client

TWILIOSID = settings.TWILIOSID
TWILIOTOKEN = settings.TWILIOTOKEN

FROM = settings.FROM
client = Client(TWILIOSID, TWILIOTOKEN)


def sendSMS(to, body):
    return client.messages.create(to=to,
                                  from_=FROM,
                                  body=body)


def sendVerificationSMS(to, key):
    return sendSMS(to, "Your verification key is: {}".format(key))
