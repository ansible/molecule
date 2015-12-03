Developer Information
=====================

* Please read the `CONTRIBUTING`_ guidelines.
* You probably want to `install from source`_.

Release Engineering
-------------------

Pre-release
^^^^^^^^^^^

* Update version in `docs/source/conf.py`.
* Edit the `CHANGELOG`_.
* Ensure tox tests pass.

Release
^^^^^^^

Tag the release and push to github.com
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. code-block:: bash

      $ git tag -a 1.0.5 -m "Version 1.0.5"
      $ git push origin 1.0.5

Upload to `PyPI`_
~~~~~~~~~~~~~~~~~

* You will require credentials to upload to `PyPI`_. Create a `~/.pypirc`:

      [distutils]
      index-servers = pypi
      [pypi]
      repository = https://pypi.python.org/pypi/molecule
      username = XXXXXXX
      password = XXXXXXX

* Install `twine`_ using `pip`.
* Upload to  `PyPI`_.

      .. code-block:: bash

         $ cd /path/to/molecule
         $ rm -rf dist/
         $ python setup.py sdist bdist_wheel
         $ twine upload dist/*


Update Molecule.ReadTheDocs.org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `curl -X POST https://readthedocs.org/build/molecule` causes a rebuild of the docsite.
* This will be a post-commit hook from the public git repository.

Post-release
^^^^^^^^^^^^

* Comment/close any relevant `Issues`_.
* Announce the release.

Roadmap
-------

* See `Issues`_ on Github.com.

.. _`PyPI`: https://pypi.python.org/pypi/molecule
.. _`ISSUES`: https://github.com/metacloud/molecule/issues
.. _`CONTRIBUTING`: https://github.com/metacloud/molecule/blob/master/CONTRIBUTING.rst
.. _`CHANGELOG`: https://github.com/metacloud/molecule/blob/master/CHANGELOG.rst
.. _`install from source`: http://molecule.readthedocs.org/en/latest/usage.html#installing-from-source
.. _`twine`: https://pypi.python.org/pypi/twine
