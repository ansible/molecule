Managing the Changelog
======================

This directory contains "newsfragments" which are short files that contain a
small **ReStructuredText**-formatted text that will be added to the next
``CHANGELOG``.

The ``CHANGELOG`` will be read by users, so this description should be aimed to
molecule users instead of describing internal changes which are only relevant
to the developers.

Make sure to use full sentences with correct case and punctuation, for example:

.. code-block:: rst

    Fix broken output of non-ascii messages produced by the ``warnings`` module.

Each file should be named like ``<ISSUE>.<TYPE>.rst``, where ``<ISSUE>`` is an
issue number, and ``<TYPE>`` is one of:

* ``feature``: new user facing features, like new command-line options and new behavior.
* ``bugfix``: fixes a reported bug.
* ``doc``: documentation improvement, like rewording an entire session or adding missing docs.
* ``deprecation``: feature deprecation.
* ``removal``: feature removal.
* ``trivial``: fixing a small typo or internal change that might be noteworthy.

So for example: ``123.feature.rst``, ``456.bugfix.rst``.

If your PR fixes an issue, use that number here. If there is no issue, then
after you submit the PR and get the PR number you can add a changelog using
that instead.

If you are not sure what issue type to use, don't hesitate to ask in your
change request.

``towncrier`` preserves multiple paragraphs and formatting (code blocks, lists,
and so on), but for entries other than ``features`` it is usually better to
stick to a single paragraph to keep it concise. 

You can run ``tox -e changelog-check`` to see the drafted output of what
``towncrier`` will generate (no file changes made). You can run the real
generation with ``tox -e changelog``.
