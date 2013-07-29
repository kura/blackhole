=====================
:mod:`blackhole.opts`
=====================

.. module:: blackhole.opts
    :platform: Unix
    :synopsis: Opts
.. moduleauthor:: Kura <kura@kura.io>

Command line options for the blackhole
server.

Also creates a list of available ports for the server to be
run on, based on configuration and responds with the help
menu when requested or invalid options are given.

blackhole.opts
==============

.. autofunction:: ports()

.. autofunction:: workers()

.. autofunction:: print_help(file)