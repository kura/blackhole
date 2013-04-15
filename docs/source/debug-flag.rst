==========
Debug Flag
==========

After much debate and several emails from developers a debug flag has been
added to blackhole.

You can enable debug using command line options :ref:`configuration_options`
or via the configuration file :ref:`configuration_file_example`.

Enabling the debug flag will log all incoming and outgoing commands to the
blackhole log file as well as all data sent after a `DATA` command.

Each connection/email gets it's own unique identifier, this indentifier
uses only hexidecimal characters and is 10 character in length, which means
at some point the identifier will be reused.

Example debug output
====================

::

    2013-04-14 07:30:30,788 - Connection from '127.0.0.1'
    2013-04-14 07:30:31,813 - [9AF260AB7F] RECV: HELO
    2013-04-14 07:30:31,814 - [9AF260AB7F] SEND: 250 2.5.0 OK, done
    2013-04-14 07:30:35,074 - [9AF260AB7F] RECV: MAIL FROM:<1@1.com>
    2013-04-14 07:30:35,075 - [9AF260AB7F] SEND: 250 2.5.0 OK, done
    2013-04-14 07:30:38,402 - [9AF260AB7F] RECV: RCPT TO:<2@2.com>
    2013-04-14 07:30:38,402 - [9AF260AB7F] SEND: 250 2.5.0 OK, done
    2013-04-14 07:30:40,573 - [9AF260AB7F] RECV: DATA
    2013-04-14 07:30:40,573 - [9AF260AB7F] SEND: 354 3.5.4 Start mail input; end with <CRLF>.<CRLF>
    2013-04-14 07:30:47,143 - [9AF260AB7F] RECV: From: <1@1.com>
    2013-04-14 07:30:52,181 - [9AF260AB7F] RECV: To: <2@2.com>
    2013-04-14 07:30:54,647 - [9AF260AB7F] RECV: Subject: Testing debug
    2013-04-14 07:30:56,550 - [9AF260AB7F] RECV: Hi 2@2.com
    2013-04-14 07:30:57,372 - [9AF260AB7F] RECV: This is a debug message
    2013-04-14 07:30:58,286 - [9AF260AB7F] RECV: .
    2013-04-14 07:30:58,287 - [9AF260AB7F] SEND: 250 2.5.0 OK, done
    2013-04-14 07:31:04,023 - [9AF260AB7F] RECV: QUIT
    2013-04-14 07:31:04,024 - [9AF260AB7F] SEND: 221 2.2.1 Thank you for speaking to me
    2013-04-14 07:31:04,024 - Closing
