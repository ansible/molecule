***
FAQ
***

Why does Molecule make so many shell calls?
===========================================

Ansible provides a python API.  However, it is not intended for
`direct consumption`_.  We wanted to focus on making Molecule useful, so our
efforts were spent consuming Ansible's CLI.

Since we already consume Ansible's CLI, we decided to call additional binaries
through their respective CLI.

.. note::

    This decision may be reevaluated later.

.. _`direct consumption`: http://docs.ansible.com/ansible/dev_guide/developing_api.html

Why does Molecule only support ansible 2.2 and 2.3?
===================================================

* Ansible 2.2 is the first good release in the Ansible 2 lineup.
* The modules needed to support the drivers did not exist pre 2.2 or were not
  sufficient.

Why are playbooks used to provision instances?
==============================================

Simplicity.  Ansible already supports numerous cloud providers.  Too much time
was spent in Molecule v1, re-implementing a feature that already existed in the
core Ansible modules.

Have you thought about using Ansible's python API instead of playbooks?
=======================================================================

This was `evaluated`_ early on.  It was a toss up.  It would provide simplicity
in some situations and complexity in others.  Developers know and understand
playbooks.  Decided against a more elegant and sexy solution.

.. _`evaluated`: https://github.com/kireledan/molecule/tree/playbook_proto

Why are there multiple scenario directories and molecule.yml files?
===================================================================

Again, simplicity.  Rather than defining an all encompassing config file opted
to normalize.  Molecule simply loops through each scenario applying the
scenario's molecule.yml.

.. note::

    This decision may be reevaluated later.

Are there similar tools to Molecule?
====================================

* Ansible's own `Testing Strategies`_
* `ansible-test`_ (`abandoned`_?)
* `RoleSpec`_

.. _`Testing Strategies`: http://docs.ansible.com/ansible/test_strategies.html
.. _`ansible-test`: https://github.com/nylas/ansible-test
.. _`abandoned`: https://github.com/nylas/ansible-test/issues/14
.. _`RoleSpec`: https://github.com/nickjj/rolespec
