"""blackhole.data - Provides SMTP response codes and methods
for returning the correct response code.

This module contains all usable SMTP response codes for
returning through the socket.
It also provides mechanisms for picking response codes
that mean a mail message has been accepted, rejected or
that the server is offline.
"""

import random

from tornado.options import options


RESPONSES = {
    '220': "OK",
    '221': "Thank you for speaking to me",
    '250': "OK",
    '251': "OK, user not local, will forward",
    '252': "OK, cannot VRFY user but will attempt delivery",
    '253': "OK, messages pending",
    '354': "Start mail input; end with <CRLF>.<CRLF>",
    '355': "Octet-offset is the transaction offset",
    '421': "Service not available, closing transmission channel",
    '450': "Requested mail action not taken: mailbox unavailable",
    '451': "Requested action aborted: local error in processing",
    '452': "Requested action not taken: insufficient system storage",
    '454': "TLS not available due to temporary reason",
    '458': "Unable to queue message",
    '459': "Not allowed: unknown reason",
    '500': "Command not recognized",
    '501': "Syntax error, no parameters allowed",
    '502': "Command not implemented",
    '503': "Bad sequence of commands",
    '504': "Command parameter not implemented",
    '521': "Machine does not accept mail",
    '530': "Must issue a STARTTLS command first",
    '534': "Authentication mechanism is too weak",
    '538': "Encryption required for requested authentication mechanism",
    '550': "Requested action not taken: mailbox unavailable",
    '551': "User not local",
    '552': "Requested mail action aborted: exceeded storage allocation",
    '553': "Requested action not taken: mailbox name not allowed",
    '554': "Transaction failed",
    '571': "Blocked",
}

ACCEPT_RESPONSES = ('250', '251', '252', '253')

# Bounce responses
BOUNCE_RESPONSES = ('421', '431', '450', '451', '452',
                    '454', '458', '459', '521',
                    '534', '550', '551', '552',
                    '553', '554', '571')

# Machine does not accept mail
OFFLINE_RESPONSES = ('521',)

# Server unavailable
UNAVAILABLE_RESPONSES = ('421',)

# Random responses
RANDOM_RESPONSES = ACCEPT_RESPONSES + BOUNCE_RESPONSES

EHLO_RESPONSES = ("250-OK", "250-SIZE 512000",
                  "250-VRFY", "250-STARTTLS",
                  "250-ENHANCEDSTATUSCODES", "250-8BITMIME",
                  "250 DSN")


def response(response=None):
    """Return an SMTP response code and message.
    'response' an string refering to the code
    you wish to return."""
    if response is not None:
        return response_message(response)
    else:
        return response_message(get_response())


def get_response():
    """
    Get our response from available responses
    based on configuration settings.
    """
    if options.mode == "random":
        return random_choice(RANDOM_RESPONSES)
    elif options.mode == "bounce":
        return random_choice(BOUNCE_RESPONSES)
    elif options.mode == "offline":
        return random_choice(OFFLINE_RESPONSES)
    elif options.mode == "unavailable":
        return random_choice(UNAVAILABLE_RESPONSES)
    else:
        return random_choice(ACCEPT_RESPONSES)


def random_choice(response_list):
    """
    Pick a random choice for the configured choices
    dictionary.

    'response_list' is a list of available response
    types from 'blackhole.data', this can be:
    - ACCEPT_RESPONSES
    - BOUCNE_RESPONSES
    - OFFLINE_RESPONSES
    - UNAVAILABLE_RESPONSES
    - RANDOM_RESPONSES
    """
    choices = []
    choices.extend(k for k, v in enumerate(response_list))
    rand = random.choice(choices)
    return response_list[rand]


def response_message(response):
    """Format our response in ESMTP format.

    'response' is a string containing the
    reponse code you wish to return."""
    response = str(response)
    message = RESPONSES[response]
    smtp_code = response
    return "%s %s\r\n" % (smtp_code, message)
