# (The MIT License)
#
# Copyright (c) 2013-2017 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides utility functionality."""

import codecs
import os
import pathlib
import random
import socket
import time


__all__ = ('blackhole_config_help', 'mailname', 'message_id', 'get_version')


class Singleton(type):
    """Singleton."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Override the __call__ method."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


def mailname(mailname_file='/etc/mailname'):
    """
    Fully qualified domain name for HELO and EHLO.

    :param str mailname_file: A path to the mailname file. Default:
                              ``/etc/mailname``.
    :returns: A domain name.
    :rtype: :py:obj:`str`

    .. note::

       Prefers content of `mailname_file`, falls back on
       :py:func:`socket.getfqdn` if `mailname_file` does not exist or cannot be
       opened for reading.
    """
    mailname_file = pathlib.PurePath(mailname_file)
    if os.access(mailname_file, os.R_OK):
        mailname_content = codecs.open(mailname_file,
                                       encoding='utf-8').readlines()
        if len(mailname_content) == 0:
            return socket.getfqdn()
        mailname_content = mailname_content[0].strip()
        if mailname_content != '':
            return mailname_content
    return socket.getfqdn()


def message_id(domain):
    """
    Return a string suitable for RFC 2822 compliant Message-ID.

    :param str domain: A fully qualified domain.
    :returns: An RFC 2822 compliant Message-ID.
    :rtype: :py:obj:`str`
    """
    timeval = int(time.monotonic() * 100)
    pid = os.getpid()
    randint = random.getrandbits(64)
    return '<{0}.{1}.{2}@{3}>'.format(timeval, pid, randint, domain)


def get_version():
    """
    Extract the __version__ from a file without importing it.

    :return: The version that was extracted.
    :rtype: :py:obj:`str`
    :raises AssertionError: When a version cannot be determined.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(pathlib.PurePath(path),
                            pathlib.PurePath('__init__.py'))
    if not os.access(filepath, os.R_OK):
        raise OSError('Cannot open __init__.py file for reading')
    with codecs.open(filepath, encoding='utf-8') as fp:
        for line in fp:
            if line.startswith('__version__'):
                try:
                    _, vers = line.split('=')
                except ValueError:
                    msg = 'Cannot extract version from __version__'
                    raise AssertionError(msg)
                version = vers.strip().replace('"', '').replace("'", '')
                try:
                    major, minor, patch = version.split('.')
                    digits = (major.isdigit(), minor.isdigit(),
                              patch.isdigit())
                    if not all(digits):
                        msg = ('{0} is not a valid version '
                               'number').format(version)
                        raise AssertionError(msg)
                except ValueError:
                    msg = '{0} is not a valid version number'.format(version)
                    raise AssertionError(msg)
                return version
    raise AssertionError('No __version__ assignment found')


class Formatter:
    bold = '\033[1m'
    under = '\033[4m'
    reset = '\033[0m'


formatting = Formatter()

blackhole_config_help = '''BLACKHOLE_CONFIG(1)

{f.bold}NAME{f.reset}
       blackhole_config - the config file format for the Blackhole MTA

{f.bold}DESCRIPTION{f.reset}
       This manual page documents the {f.bold}Blackhole{f.reset} configuration file format and
       options.

{f.bold}OPTIONS{f.reset}
    These are all available options for the configuration file, their default
    values and information on what the options actually do.

    The file format is a simple {f.under}attribute = value{f.reset} style, an example is shown
    below.

        # This is a comment.
        listen = :25  # This is an inline comment.
        user = kura
        group = kura

    {f.bold}listen{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}listen{f.reset} = {f.under}[address]:port [mode=MODE] [delay=DELAY]{f.reset}

        {f.bold}Default{f.reset}
            127.0.0.1:25,  127.0.0.1:587, :::25, :::587
            IPv6 listeners are only enabled if IPv6 is supported.

        {f.bold}Optional{f.reset}
            {f.under}mode={f.reset} and {f.under}delay={f.reset} -- allows setting a response mode and delay per
            listener.

        The {f.under}mode={f.reset} and {f.under}delay={f.reset} flags allow specific ports to act in different ways.
        i.e. you could accept all mail on 10.0.0.1:25 and bounce it all on
        10.0.0.2:25, as below.

            listen = 10.0.0.1:25 mode=accept, 10.0.0.2:25 mode=bounce

        The {f.under}mode={f.reset} and {f.under}delay={f.reset} flags may also be specified together, as required.

            listen = 10.0.0.1:25 mode=accept delay=5, 10.0.0.2:25 mode=bounce delay=10

        The flags accept the same options as {f.under}dynamic-switches{f.reset}, including setting
        a delay range.

                                            ----

    {f.bold}tls_listen{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}tls_listen{f.reset} = {f.under}[address]:port [mode=MODE] [delay=DELAY]{f.reset}

        {f.bold}Default{f.reset}
            None

        {f.bold}Optional{f.reset}
            {f.under}mode={f.reset} and {f.under}delay={f.reset} -- allows setting a response mode and delay per
            listener.


        :465 is equivalent to listening on port 465 on all IPv4 addresses and
        :::465 is equivalent to listening on port 465 on all IPv6 addresses.

        Multiple addresses and ports can be listed on a single line.

            tls_listen = 10.0.0.1:465, 10.0.0.2:465, :465, :::465

        The {f.under}mode={f.reset} and {f.under}delay={f.reset} flags allow specific ports to act in different ways.
        i.e. you could accept all mail on 10.0.0.1:465 and bounce it all on
        10.0.0.2:465, as below.

            tls_listen = 10.0.0.1:465 mode=accept, 10.0.0.2:465 mode=bounce

        The {f.under}mode={f.reset} and {f.under}delay={f.reset} flags may also be specified together, as required.

            tls_listen = 10.0.0.1:465 mode=accept delay=5, 10.0.0.2:465 mode=bounce delay=10

        The flags accept the same options as {f.under}dynamic-switches{f.reset}, including setting
        a delay range.

                                                   ----

    {f.bold}user{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}user{f.reset} = {f.under}user{f.reset}

        {f.bold}Default{f.reset}
            The current Linux user

        Blackhole will set it's process owner to the value provided with this
        option. Ports below 1024 require sudo or root privileges, this option
        is available so that the process can be started, listen on privileged
        ports and then give up those privileges.

                                                    ----

    {f.bold}group{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}group{f.reset} = {f.under}group{f.reset}

        {f.bold}Default{f.reset}
            The primary group of the current Linux user

        Blackhole will set it's process group to the value provided with this
        option.

                                                    ----

    {f.bold}pidfile{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}pidfile{f.reset} = {f.under}/path/to/file.pid{f.reset}

        {f.bold}Default{f.reset}
            /tmp/blackhole.pid

        Blackhole will write it's Process ID to this file, allowing you to
        easily track the process and send signals to it.

                                                    ----

    {f.bold}timeout{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}timeout{f.reset} = {f.under}seconds{f.reset}

        {f.bold}Default{f.reset}
            60 -- Maximum value of 180 seconds.

        This is the amount of time to wait for a client to send data. Once the
        timeout value has been reached with no data being sent by the client,
        the connection will be terminated and a 421 Timeout message will be
        sent to the client.

        Helps mitigate DoS risks.

                                                    ----

    {f.bold}tls_cert{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}tls_cert{f.reset} = {f.under}/path/to/certificate.pem{f.reset}

        {f.bold}Default{f.reset}
            None

        The certificate file in x509 format for wrapping a connection in
        SSL/TLS.

                                                    ----

    {f.bold}tls_key{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}tls_key{f.reset} = {f.under}/path/to/private.key{f.reset}

        {f.bold}Default{f.reset}
            None

        The private key of the tls_cert.

                                                    ----

    {f.bold}tls_dhparams{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}tls_dhparams{f.reset} = {f.under}/path/to/dhparams.pem{f.reset}

        {f.bold}Default{f.reset}
            None

        File containing Diffie Hellman ephemeral parameters for ECDH ciphers.

                                                    ----

    {f.bold}delay{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}delay{f.reset} = {f.under}seconds{f.reset}

        {f.bold}Default{f.reset}
            0 -- Maximum value of 60 seconds.

        Time to delay before returning a response to a completed DATA command.
        You can use this to delay testing or simulate lag.

                                                    ----

    {f.bold}mode{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}mode{f.reset} = {f.under}accept | bounce | random{f.reset}

        {f.bold}Default{f.reset}
            accept

                                                        ----

    {f.bold}max_message_size{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}max_message_size{f.reset} = {f.under}bytes{f.reset}

        {f.bold}Default{f.reset}
            512000 Bytes (512 KB)

        The maximum message size for a message. This includes headers and helps
        mitigate a DoS risk.

                                                    ----

    {f.bold}dynamic_switch{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}dynamic_switch{f.reset} = {f.under}true | false{f.reset}

        {f.bold}Default{f.reset}
            true

        The dynamic switch option allows you to enable or disable parsing of
        dynamic switches from email headers.

                                                    ----

    {f.bold}workers{f.reset}
        {f.bold}Syntax{f.reset}
            {f.bold}workers{f.reset} = {f.under}number{f.reset}

        {f.bold}Default{f.reset}
            1

        The workers option allows you to define how many worker processes to
        spawn to handle incoming mail. The absolute minimum is actually 2. Even
        by setting the workers value to 1, a supervisor process will always
        exist meaning that you would have 1 worker and a supervisor.
'''.format(f=formatting)  # noqa
