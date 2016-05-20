# (The MIT License)
#
# Copyright (c) 2016 Kura
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

import logging
import random


__all__ = ('Switch', )


logger = logging.getLogger('blackhole.smtp.switch')


class Switch:

    def process_header(self, line):
        """
        Process dynamic switch email headers.

        Reads x-blackhole-delay and x-blackhole-mode headers and re-configures
        on-the-fly how the email is handled based on these headers.

        https://blackhole.io/dynamic-switches.html

        :param line: An email header.
        :type line: :any:`str`
        """
        logger.debug('HEADER RECV: %s', line)
        if self.config.dynamic_switch is False:
            logger.debug('Dynamic switches disabled, ignoring')
            return
        if self._disable_dynamic_switching is True:
            logger.debug('Dynamic switches are disabled by flags option.')
            return
        key, value = line.split(':')
        key, value = key.lower().strip(), value.lower().strip()
        if key == 'x-blackhole-delay':
            self.delay = value
        if key == 'x-blackhole-mode':
            self.mode = value

    async def response_from_mode(self):
        """
        Send a response based on the configured response mode.

        https://blackhole.io/dynamic-switches.html#dynamic-delay-switches
        https://blackhole.io/configuration-options.html#mode
        https://blackhole.io/modes.html

        Response mode is configured in configuration file and can be overridden
        by email headers, if enabled.
        """
        logger.debug('MODE: %s', self.mode)
        if self.mode == 'bounce':
            key = random.choice(list(self._bounce_responses.keys()))
            await self.push(key, self._bounce_responses[key])
        elif self.mode == 'random':
            resps = {250: '2.0.0 OK: queued as {}'.format(self.message_id), }
            resps.update(self._bounce_responses)
            key = random.choice(list(resps.keys()))
            await self.push(key, resps[key])
        else:
            msg = '2.0.0 OK: queued as {}'.format(self.message_id)
            await self.push(250, msg)

    @property
    def delay(self):
        """
        Delay after the DATA command completes.

        Value is in seconds, with a maximum value of 60 seconds.

        https://blackhole.io/configuration-options.html#delay
        https://blackhole.io/dynamic-switches.html#dynamic-delay-switches

        :returns: A delay time in seconds.
        :rtype: :any:`int` or :any:`None`
        """
        if 'delay' in self.flags.keys():
            delay = self.flags['delay']
            if isinstance(delay, list):
                self._delay_range(delay)
                return self._delay
            return int(delay)
        if self._delay is not None:
            return self._delay
        if self.config.delay is not None:
            return self.config.delay
        return None

    @delay.setter
    def delay(self, values):
        logger.debug('DELAY: Dymanic delay enabled')
        value = values.split(',')
        if len(value) == 2:
            self._delay_range(value)
        elif len(value) == 1:
            self._delay_single(value[0])
        else:
            logger.debug('DELAY: Invalid value(s): %s. Skipping', values)
            return

    def _delay_range(self, value):
        """
        Generate a delay from a range provided in the email header.

        https://blackhole.io/configuration-options.html#delay
        https://blackhole.io/dynamic-switches.html#dynamic-delay-switches

        :param value: A list of minimum and maximum values as a string. i.e.
                      (10, 20).
        :type value: :any:`str`

        .. note::

           Converted from a string of a list to a list of integers.
        """
        min_delay, max_delay = value
        min_delay, max_delay = min_delay.strip(), max_delay.strip()
        try:
            min_delay = int(min_delay)
            max_delay = int(max_delay)
        except ValueError:
            logger.debug('DELAY: Unable to convert %s, %s to integers. '
                         'Skipping', min_delay, max_delay)
            self._delay = None
            return
        if min_delay < 0 or max_delay < 0:
            logger.debug('DELAY: A value is less than 0: %s, %s. Skipping',
                         min_delay, max_delay)
            self._delay = None
            return
        if min_delay > max_delay:
            logger.debug('Min cannot be greater than max')
            self._delay = None
            return
        if max_delay > self._max_delay:
            logger.debug('DELAY: %s is higher than %s. %s is the hard coded '
                         'maximum delay for security.', max_delay,
                         self._max_delay, self._max_delay)
            max_delay = self._max_delay
        self._delay = random.randint(min_delay, max_delay)
        logger.debug('DELAY: Set to %s from range %s-%s', self._delay,
                     min_delay, max_delay)
        return

    def _delay_single(self, value):
        """
        Generate a delay from a value provided in an email header.

        https://blackhole.io/configuration-options.html#delay
        https://blackhole.io/dynamic-switches.html#dynamic-delay-switches

        :param value: Time in seconds as a string.
        :type value: :any:`str`

        .. note:

           Converted from a string to an integer.
        """
        try:
            value = int(value)
        except ValueError:
            logger.debug('DELAY: Unable to convert %s to an integer. Skipping',
                         value)
            self._delay = None
            return
        logger.debug(value)
        if value < 0:
            logger.debug('DELAY: %s is less than 0. Skipping', value)
            self._delay = None
            return
        if value > self._max_delay:
            logger.debug('DELAY: %s is higher than %s. %s is the hard coded '
                         'maximum delay for security.', value, self._max_delay,
                         self._max_delay)
            self._delay = self._max_delay
            return
        logger.debug('DELAY: Set to %s', value)
        self._delay = value

    @property
    def mode(self):
        """
        How to respond to an email, based on configuration.

        Reponse is configured in the configuration file or configured from
        email headers, if configured to allow that option.

        https://blackhole.io/configuration-options.html#mode
        https://blackhole.io/dynamic-switches.html#dynamic-mode-switches

        :returns: A response mode.
        :rtype: :any:`str`
        """
        if 'mode' in self.flags.keys():
            return self.flags['mode']
        if self._mode is not None:
            return self._mode
        return self.config.mode

    @mode.setter
    def mode(self, value):
        if value not in ('accept', 'bounce', 'random'):
            logger.debug('MODE: %s is an invalid. Allowed modes: (accept, '
                         'bounce, random)', value)
            self._mode = None
            return
        logger.debug('MODE: Dynamic mode enabled. Mode set to %s', value)
        self._mode = value
