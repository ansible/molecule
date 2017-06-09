#!/usr/bin/env python
import os
from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: goss
author: Mathieu Corbin
short_description: Launch goss (https://github.com/aelsabbahy/goss) tests
description:
  - Launch goss tests.
    This module always returns `changed = false` for idempotence.
options:
  path:
    required: true
    description:
      - Test file to validate.
        The test file must be on the remote machine.
  goss_path:
    required: false
    description:
      - Path location for the goss executable.
        Default is "goss" (ie.`no absolute path,  goss executable must be available in $PATH).
  format:
    required: false
    description:
      - Output goss format.
        Goss format list : goss v --format => [documentation json junit nagios nagios_verbose rspecish tap silent].
        Default is "rspecish".
  output_file:
    required: false
    description:
      - Save the result of the goss command in a file whose path is output_file

examples:
  - name: run goss against the gossfile /path/to/file.yml
    goss:
      path: "/path/to/file.yml"

  - name: run goss against the gossfile /path/to/file.yml with nagios output
    goss:
      path: "/path/to/file.yml"
      format: "nagios"

  - name: run /usr/local/bin/goss against the gossfile /path/to/file.yml
    goss:
      path: "/path/to/file.yml"
      goss_path: "/usr/local/bin/goss"

  - name: run goss against multiple gossfiles and write the result in JSON format to /my/output/ for each file
    goss:
      path: "{{ item }}"
      format: json
      output_file : /my/output/{{ item }}
    with_items: "{{ goss_files }}"
'''


# launch goss validate command on the file
def check(module, test_file_path, output_format, goss_path):
    cmd = ""
    if output_format is not None:
        cmd = "{0} -g {1} v --format {2}".format(goss_path, test_file_path, output_format)
    else:
        cmd = "{0} -g {1} v".format(goss_path, test_file_path)
    return module.run_command(cmd)


# write goss result to output_file_path
def output_file(output_file_path, out):
    if output_file_path is not None:
        with open(output_file_path, 'w') as output_file:
            output_file.write(out)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True, type='str'),
            format=dict(required=False, type='str'),
            output_file=dict(required=False, type='str'),
            goss_path=dict(required=False, default='goss', type='str'),
        ),
        supports_check_mode=False
    )

    test_file_path = module.params['path']  # test file path
    output_format = module.params['format']  # goss output format
    output_file_path = module.params['output_file']
    goss_path = module.params['goss_path']

    if test_file_path is None:
        module.fail_json(msg="test file path is null")

    test_file_path = os.path.expanduser(test_file_path)

    # test if access to test file is ok

    if not os.access(test_file_path, os.R_OK):
        module.fail_json(msg="Test file %s not readable" % (test_file_path))

    # test if test file is not a dir
    if os.path.isdir(test_file_path):
        module.fail_json(msg="Test file must be a file ! : %s" % (test_file_path))

    (rc, out, err) = check(module, test_file_path, output_format, goss_path)

    if output_file_path is not None:
        output_file_path = os.path.expanduser(output_file_path)
        # check if output_file is a file
        if output_file_path.endswith(os.sep):
            module.fail_json(msg="output_file must be a file. Actually :  %s "
                             % (output_file_path))

        output_dirname = os.path.dirname(output_file_path)

        # check if output directory exists
        if not os.path.exists(output_dirname):
            module.fail_json(msg="directory %s does not exists" % (output_dirname))

        # check if writable
        if not os.access(os.path.dirname(output_file_path), os.W_OK):
            module.fail_json(msg="Destination %s not writable" % (os.path.dirname(output_file_path)))
        # write goss result on the output file
        output_file(output_file_path, out)

    if rc is not None and rc != 0:
        error_msg = "err : {0} ; out : {1}".format(err, out)
        module.fail_json(msg=error_msg)

    result = {}
    result['stdout'] = out
    result['changed'] = False

    module.exit_json(**result)

main()
