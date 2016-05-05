.. _todo:

..  role:: strikethrough

====
TODO
====

Things on the todo list, in no particular order.

- Implement logging to a file.
- :strikethrough:`Add pidfile tests for config to config_test and pytest.` --
  :ref:`2.0.4`
- :strikethrough:`Add socket bind tests to config_test and pytest` --
  :ref:`2.0.2`
- :strikethrough:`Dynamic mode switch  - helo, ehlo, delay verb, rcpt, mail
  from` -- :ref:`2.0.4`
- :strikethrough:`Dynamic delay switch - min and max delay range (i.e. delay
  between 10 and seconds, randomly) - helo, ehlo, delay verb, rcpt, mail
  from` -- :ref:`2.0.4`
- :strikethrough:`HELP verb` -- :ref:`2.0.2`
- :strikethrough:`Improve TLS by adding load_dh_params` -- :ref:`2.0.4`
- :strikethrough:`Add AUTH mechanism` -- :ref:`2.0.4`
- POP & IMAP -- started, progress available at
  `<https://github.com/kura/blackhole/tree/imap4>`_
- :strikethrough:`Add SMTP Submission to default interfaces` -- :ref:`2.0.14`
- :strikethrough:`Add more lists to EXPN and combine for EXPN all` --
  :ref:`2.0.14`
- :strikethrough:`Add pass= and fail= to more verbs` -- :ref:`2.0.14`
- Properly implement ``PIPELINING`` -- build responses in a list and return in
  order after ``.\r\n``
- Added base level server that can be extended, i.e. ``NOT IMPLEMENTED`` most
  features.
- Strip out :any:`blackhole.config.Config` context and make it loadable on
  creation -- allowing any config context to be passed.
- Command injection -- move HELO, EHLO etc to separate modules, allowing them
  to be injected and that injection to be overriden by a user-defined method.
- Add auth mechanisms as injectables, special injectables that, unlike the
  command inections, these are injected specially in to the auth system.

Possible future features
========================

- Greylist support
- DKIM / DomainKeys / SPF / Sender-ID after DATA command.
