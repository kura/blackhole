==========
Delay Flag
==========

The delay flag was something that was requested during the Q+A phase
when I did a talk on Blackhole.

Sadly it is a blocking call, meaning that any other connections
made to the server at that point in time will also block until
the delay is complete.

This is less of an issue when running more than one blackhole-worker
but even so it is an option that must be used cautiously.

EVery response from the server will be delayed by the amount of
seconds you specify.

You can enable delay using command line options :ref:`configuration_options`
or via the configuration file :ref:`configuration_file_example`.

