import smtplib
import atexit

import eventlet


s = smtplib.SMTP('ec2-79-125-50-71.eu-west-1.compute.amazonaws.com', 25)
msg = """To: <kura@kura.io>
From: <kura@kura.io>
Subject: Test

Hi Kura
http://taz.map-dev.tangentlabs.co.uk/o/9e277348e9d64bdc89b3f250/9e277348-e9d6-4bdc-89b3-f250dadf5e98/9e277348-e9d6-4bdc-89b3-f250fadf5456/image.gif
Go to: http://taz.map-dev.tangentlabs.co.uk/c/9e277348e9d64bdc89b3f250/9e277348-e9d6-4bdc-89b3-f250dadf5e98/9e277348-e9d6-4bdc-89b3-f250fadf5456/9e277348-e9d6-4bdc-89b3-f250fadf5456/http://www.google.co.uk/"""

def send(i):
    print "Sending: %d" % i
    s.sendmail('kura@kura.io', 'kura@kura.io', msg)

pool = eventlet.GreenPool(10)
i = 1
while True:
    pool.spawn_n(send, i)
    i += 1

@atexit.register
def close():
    s.close()
