.. _configuration-file-example:

==========================
Configuration file example
==========================

A list of all available options, their default values on what the options do is
available on the :ref:`configuration-options` document.

You can download a copy of this example file from
`GitHub <https://github.com/kura/blackhole/blob/master/example.conf>`_.

.. code-block:: ini
   :linenos:

    #
    # Listen for IPv4 and IPv6 connections.
    #
    # Format:- HOST:PORT, HOST2:PORT2
    # Separate multiple listeners with commas.
    #
    # listen=:25  is equivalent to listening on all IPv4 addresses
    # listen=:::25  is equivalent to listen on all IPv6 addresses
    #
    # listen=0.0.0.0:25
    # listen=0.0.0.0:1025, fe80::a00:27ff:fe8c:9c6e:1025
    #
    listen=127.0.0.1:25

    #
    # Listen IPv4 and IPv6 SSL/TLS connections.
    #
    # Format:- HOST:PORT, HOST2:PORT2
    # Separate multiple listeners with commas.
    #
    # tls_listen=:465  is equivalent to listening on all IPv4 addresses
    # tls_listen=:::465  is equivalent to listen on all IPv6 addresses
    #
    # tls_listen=0.0.0.0:465, fe80::a00:27ff:fe8c:9c6e:465

    #
    # User to run blackhole as.
    # Defaults to current user.
    #
    # user=blackhole

    #
    # Group to run blackhole as.
    # Defaults to current group.
    #
    # group=blackhole

    #
    # Timeout after no data has been received in seconds.
    # Defaults to 60 seconds. Cannot be more than 180 seconds for security
    # (denial of service).
    #
    # timeout=45
    # timeout=180

    #
    # TLS certificate location.
    # Certificate should be x509 format.
    #
    # tls_cert=/etc/ssl/blackhole.crt

    #
    # TLS key file for x509 certificate.
    #
    # tls_key=/etc/ssl/blackhole.key

    #
    # Diffie Hellman ephemeral parameters.
    # openssl dhparam 4096
    #
    # tls_dhparams=/etc/ssl/blackhole.dhparams.pem

    #
    # Delay for X seconds after the DATA command before sending the final
    # response.
    #
    # Must be less than timeout.
    # Time is in seconds and cannot be set above 60 seconds for security
    # (denial of service).
    # Non-blocking - won't affect other connections.
    #
    # delay=10

    #
    # Response mode for the final response after the DATA command.
    #
    # accept (default) - all emails are accepted with 250 code.
    # bounce - bounce all emails with a random code.
    # random - randomly accept or bounce.
    #
    # Bounce codes:
    # 450: Requested mail action not taken: mailbox unavailable
    # 451: Requested action aborted: local error in processing
    # 452: Requested action not taken: insufficient system storage
    # 458: Unable to queue message
    # 521: Machine does not accept mail
    # 550: Requested action not taken: mailbox unavailable
    # 551: User not local
    # 552: Requested mail action aborted: exceeded storage allocation
    # 553: Requested action not taken: mailbox name not allowed
    # 571: Blocked
    #
    # mode=accept

    #
    # Maximum message size in bytes.
    # Default 512000 bytes (512 KB).
    #
    # max_message_size=1024000

    #
    # Pid file location.
    # Default: /tmp/blackhole.pid
    #
    # pidfile=/var/run/blackhole.io

    #
    # Dynamic switches
    # Allows switching how blackhole responds to an email and delays responding
    # based on a header.
    #
    # https://blackhole.io/dynamic-switches.html#dynamic-switches
    #
    # Default: true
    #
    # dynamic_switch=false
