import urllib.request
import datetime
import ssl
import os

def send(phones):
    if len(phones) > 0:
        try:
            phoneNumbers = ';'.join(phones)
            textMessage = 'TK {1} {0}'.format(os.uname()[1], datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            textRequest = 'https://smsc.ru/sys/send.php?login={Login}&psw={Password}&sender=PROMEAT&phones={PhoneNumbers}&mes={TextMessage}'
                .format(Login='xxxxxx', Password='xxxxx', PhoneNumbers=phoneNumbers, TextMessage=textMessage)
            urllib.request.urlopen(textRequest, context=ssl._create_unverified_context())
        except Exception as e:
            print(e)
