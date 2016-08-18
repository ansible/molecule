***************
Bash Completion
***************

A bash completion script is provided in the asset directory. It auto-completes
the subcommands, options and dynamic arguments such as platform, providers, and
hosts.

Linux users
===========

The script will install globally in ``etc/bash_completion.d``.

OS X users
==========

For OS X user, you must do the following to enable the script:

.. code-block:: bash

  $ USER_BASH_COMPLETION_DIR=~/bash_completion.d
  $ mkdir -p "${USER_BASH_COMPLETION_DIR}"
  $ wget -O "${USER_BASH_COMPLETION_DIR}/molecule" \
    https://github.com/metacloud/molecule/blob/master/asset/bash_completion/molecule.bash-completion.sh

and in ``~/.bash_profile``, add the following:

.. code-block:: bash

  if [ -d ~/bash_completion.d ]; then
    . ~/bash_completion.d/*
  fi

if you are using ``brew`` you can use ``${BASH_COMPLETION_DIR}`` instead of
``${USER_BASH_COMPLETION_DIR}``.
