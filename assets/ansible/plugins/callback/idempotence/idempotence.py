from __future__ import (absolute_import, division, print_function)


class CallbackModule(object):
    """
    Callback module to use for Molecule idempotence test.
    Only the tasks that have changed since last run are displayed.
    """

    def __init__(self):
        self.changed_items = []
        self.current = None

    def runner_on_ok(self, host, res):
        if res['changed']:
            self.changed_items.append(self.current)

    def playbook_on_task_start(self, name, is_conditional):
        self.current = name

    def playbook_on_stats(self, stats):
        for item in self.changed_items:
            print('NI: {}'.format(item))
