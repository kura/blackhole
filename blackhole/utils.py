import os
import random
import socket
import time


def mailname():
    """
    Return a mailname for HELO.
    Reads /etc/mailname if present
    and falls back to socket.getfqdn
    """
    mailname_file = "/etc/mailname"
    if os.path.exists(mailname_file):
        mnc = open(mailname_file, 'r').read().strip()
        if mnc != "":
            return mnc
    return socket.getfqdn()


def message_id():
    """
    Return a globally unique random string in RFC 2822 Message-ID format.

    Optional uniq string will be added to strengthen uniqueness if given.
    """
    def id_generator():
        i = 0
        while True:
            yield i
            i += 1
    datetime = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    pid = os.getpid()
    rand = random.randrange(2**31L-1)
    return '<{}.{}.{}.{}@{}>'.format(datetime, pid, rand,
                                     id_generator().next(), mailname())
