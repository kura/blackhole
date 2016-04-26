.. _command-line-options:

====================
Command line options
====================

Configuration options can be passed via the command line
as below:

-h			show this help message and exit
-v			show program's version number and exit
-c FILE		override the default configuration options
-t			perform a configuration test and exit
-d			enable debugging mode
-b			run in the background
-ls         Disable :any:`ssl.OP_SINGLE_DH_USE` and
            :any:`ssl.OP_SINGLE_ECDH_USE`. Reduces CPU overhead at the expense
            of security. Don't use this option unless you really need to. --
            added in :ref:`2.0.13`

For information on the configuration options, their default values and what
each option does, please see the :ref:`configuration-options` document and,
for an example configuration file see :ref:`configuration-file-example`.
