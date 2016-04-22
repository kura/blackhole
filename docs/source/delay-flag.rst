.. _delay_flag:

==========
Delay Flag
==========

The delay flag was something that was requested during the Q+A phase
when I presented a talk on Blackhole.

The server will delay it's response after the \\r\\n.\\r\\n line after the DATA
verb.

The blackhole server is hardcoded to have a maximum delay of 60 seconds for
security (denial of service).

As an example::

    ...
    ...
    DATA
    354 End data with <CR><LF>.<CR><LF>
    To: <test@blackhole.io>
    From: <test@blackhole.io>
    Subject: Test

    Random test message.
    .

    - THE SERVER RUNS DELAY FUNCTIONALITY -

    250 2.0.0 OK: queued as <20160418202241.7778.853458045.0@blackhole.io>
    QUIT

You can enable delay using the configuration file option
:ref:`configuration-file-example` or using :ref:`dynamic-switches`.
