***
FAQ
***

Why is my idempotence action failing?
=====================================

It is important to understand that Molecule does not do anything further than
the default functionality of Ansible when determining if your tasks are
idempotent or not. Molecule will simply run the converge action twice and check
against Ansible's standard output.

Therefore, if you are seeing idempotence failures, it is typically related to
the underlying Ansible report and not Molecule.

If you are facing idempotence failures and intend to raise a bug on our issue
tracker, please first manually run ``molecule converge`` twice and confirm that
Ansible itself is reporting task idempotence (changed=0).

Why does Molecule make so many shell calls?
===========================================

Ansible provides a Python API.  However, it is not intended for
`direct consumption`_.  We wanted to focus on making Molecule useful, so our
efforts were spent consuming Ansible's CLI.

Since we already consume Ansible's CLI, we decided to call additional binaries
through their respective CLI.

.. note::

    This decision may be reevaluated later.

.. _`direct consumption`: https://docs.ansible.com/ansible/latest/dev_guide/developing_api.html

Why does Molecule only support Ansible versions 2.2 and later?
==============================================================

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

.. _`Testing Strategies`: https://docs.ansible.com/ansible/latest/reference_appendices/test_strategies.html
.. _`ansible-test`: https://github.com/nylas/ansible-test
.. _`abandoned`: https://github.com/nylas/ansible-test/issues/14
.. _`RoleSpec`: https://github.com/nickjj/rolespec

Can I run Molecule processes in parallel?
=========================================

Please see :ref:`parallel-usage-example` for usage.

Can I specify random instance IDs in my molecule.yml?
=====================================================

This depends on the CI provider but the basic recipe is as follows.

Setup your ``molecule.yml`` to look like this:

.. code-block:: yaml

  platforms:
    - name: "instance-${INSTANCE_UUID}"

Then in your CI provider environment, for example, Gitlab CI, setup:

.. code-block:: yaml

  variables:
    INSTANCE_UUID: "$CI_JOB_ID"

Where ``CI_JOB_ID`` is the random variable that Gitlab provides.

Molecule will resolve the ``INSTANCE_UUID`` environment variable when creating
and looking up the instance name. You can confirm all is in working order by
running ``molecule list``.

Can I test Ansible Collections with Molecule?
=============================================

This is not currently officially supported. Also, collections remain in "tech
preview" status. However, you can take a look at `this blog post`_ outlining a
workable "DIY" solution as a stop gap for now.

.. _`this blog post`: https://www.jeffgeerling.com/blog/2019/how-add-integration-tests-ansible-collection-molecule

Does Molecule support monorepos?
================================

Yes, roles contained in a `monorepo`_ with other roles are automatically picked
up and ``ANSIBLE_ROLES_PATH`` is set accordingly. See `this page`_ for more
information.

.. _`monorepo`: https://en.wikipedia.org/wiki/Monorepo
.. _`this page`: https://molecule.readthedocs.io/en/stable/examples.html#monolith-repo

How can I add development/testing-only dependencies?
=====================================================

Sometimes, it's desirable to only run a dependency role when developing your
role with molecule, but not impose a hard dependency on the role itself; for
example when you rely on one of its side effects. This can be achieved by an
approach like this in your role's ``meta/main.yml``:

::

  ---
  dependencies:
    - role: <your-dependee-role>
      when: lookup('env', 'MOLECULE_FILE')
