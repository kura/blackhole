============================
:mod:`blackhole.application`
============================

.. module:: blackhole.application
    :platform: Unix
    :synopsis: Application
.. moduleauthor:: Kura <kura@kura.io>

This module is responsible for configuring, managing and running the blackhole
server instance and it's children.

It is the Python entry-point for the blackhole binary.

blackhole.application
=====================

.. function:: set_action()

    Figure out what action to perform based on arguments passed on the command
    line.

    start, stop or status

.. function:: set_options()

    Set our default options, overriding them as required i.e. for SSL.

    Also outputs warning message when using Debug and Delay modes and is
    responsible for warning about deprecated options.

.. function:: daemon(action)

    Trigger the daemon, run the action command and return the daemon object
    if required.

    'action' is a string, either start, stop or status
    Returns an instance of deiman.Deiman

.. function:: fork()

    Fork the processes off, set process titles (master, worker) and return
    and ioloop.

    Returns an instance of tornado.ioloop.IOLoop


.. function:: run()

    The run method is what actually spawns and manages blackhole.
