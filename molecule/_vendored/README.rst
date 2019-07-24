Code temporary imported from future versions of our dependencies.

Use example: using latest version of an Ansible module from ansible-devel
until the same code is released and our minimal Ansible version matches it.

Code backported this way should not shadow original one and should be
used only by Molecule own code, not the tested playbooks. Not doing this
would risk getting different results in testing than in production use.
