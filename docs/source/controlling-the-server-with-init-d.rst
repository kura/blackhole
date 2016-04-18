.. _controlling-the-server-with-init-d:

=======================================
Controlling the server with init.d/rc.d
=======================================

Installating the init.d/rc.d scripts
====================================

The init script depends on */etc/blackhole.conf* being in place and configured.

Blackhole comes with a script that works with init.d/rc.d, to install it copy it
from the *init.d/YOUR_DISTRO* folder in the root directory of this project to
*/etc/init.d/*.

The init scripts can be found `here`_.

.. _here: https://github.com/kura/blackhole/tree/master/init.d

i.e. for Debian/Ubuntu users, mv the file from *init.d/debian-ubuntu/* to */etc/init.d/*.

Then make sure it's executable

.. code-block:: bash

  chmod +x /etc/init.d/blackhole

To make blackhole start on a reboot use the following::

  update-rc.d blackhole defaults
