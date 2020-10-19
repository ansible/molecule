"""Base definition for Ansible Galaxy dependencies."""
from molecule import util
from molecule.dependency.ansible_galaxy.collections import Collections
from molecule.dependency.ansible_galaxy.roles import Roles
from molecule.dependency.base import Base


class AnsibleGalaxy(Base):
    """
    :std:doc:`Galaxy <galaxy/user_guide>` is the default dependency manager.

    Additional options can be passed to ``ansible-galaxy install`` through the
    options dict.  Any option set in this section will override the defaults.

    .. note::

        Molecule will remove any options matching '^[v]+$', and pass ``-vvv``
        to the underlying ``ansible-galaxy`` command when executing
        `molecule --debug`.

    .. code-block:: yaml

        dependency:
          name: galaxy
          options:
            ignore-certs: True
            ignore-errors: True
            role-file: requirements.yml
            requirements-file: collections.yml

    Use "role-file" if you have roles only. Use the "requirements-file" if you
    need to install collections. Note that, with Ansible Galaxy's collections
    support, you can now combine the two lists into a single requirement if your
    file looks like this

    .. code-block:: yaml

        roles:
          - dep.role1
          - dep.role2
        collections:
          - ns.collection
          - ns2.collection2

    If you want to combine them, then just point your ``role-file`` and
    ``requirements-file`` to the same path. This is not done by default because
    older ``role-file`` only required a list of roles, while the collections
    must be under the ``collections:`` key within the file and pointing both to
    the same file by default could break existing code.

    The dependency manager can be disabled by setting ``enabled`` to False.

    .. code-block:: yaml

        dependency:
          name: galaxy
          enabled: False

    Environment variables can be passed to the dependency.

    .. code-block:: yaml

        dependency:
          name: galaxy
          env:
            FOO: bar
    """

    def __init__(self, config):
        """Construct AnsibleGalaxy."""
        super(AnsibleGalaxy, self).__init__(config)
        self.invocations = [Roles(config), Collections(config)]

    def execute(self):
        for invoker in self.invocations:
            invoker.execute()

    def _has_requirements_file(self):
        has_file = False
        for invoker in self.invocations:
            has_file = has_file or invoker._has_requirements_file()
        return has_file

    @property
    def default_env(self):
        e = {}
        for invoker in self.invocations:
            e = util.merge(e, invoker.default_env)
        return e

    @property
    def default_options(self):
        opts = {}
        for invoker in self.invocations:
            opts = util.merge(opts, invoker.default_opts)
        return opts
