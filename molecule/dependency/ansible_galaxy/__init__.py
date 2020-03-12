from molecule.dependency.base import Base
from molecule.dependency.ansible_galaxy.roles import Roles
from molecule.dependency.ansible_galaxy.collections import Collections


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
        for subtype in self.invocations:
            has_file = (has_file or subtype._has_requirements_file())
        return has_file
