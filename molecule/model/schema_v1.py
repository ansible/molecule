#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import cerberus
import cerberus.errors

base_schema = {
    'ansible': {
        'type': 'dict',
        'schema': {
            'config_file': {
                'type': 'string',
            },
            'playbook': {
                'type': 'string',
            },
            'raw_env_vars': {
                'type': 'dict',
                'keyschema': {
                    'type': 'string',
                    'regex': '^[A-Z0-9_-]+$',
                },
            },
            'extra_vars': {
                'type': 'string',
            },
            'verbose': {
                'type': 'boolean',
            },
            'become': {
                'type': 'boolean',
            },
            'tags': {
                'type': 'string',
            },
        }
    },
    'driver': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
        }
    },
    'vagrant': {
        'type': 'dict',
        'schema': {
            'platforms': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                        },
                        'box': {
                            'type': 'string',
                        },
                        'box_version': {
                            'type': 'string',
                        },
                        'box_url': {
                            'type': 'string',
                        },
                    }
                }
            },
            'providers': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                        },
                        'type': {
                            'type': 'string',
                        },
                        'options': {
                            'type': 'dict',
                        },
                    }
                }
            },
            'instances': {
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'name': {
                            'type': 'string',
                        },
                        'ansible_groups': {
                            'type': 'list',
                            'schema': {
                                'type': 'string',
                            }
                        },
                        'interfaces': {
                            'type': 'list',
                            'schema': {
                                'type': 'dict',
                            }
                        },
                        'raw_config_args': {
                            'type': 'list',
                            'schema': {
                                'type': 'string',
                            }
                        },
                    }
                }
            },
        }
    },
    'verifier': {
        'type': 'dict',
        'schema': {
            'name': {
                'type': 'string',
            },
            'options': {
                'type': 'dict',
            },
        }
    },
}


def validate(c):
    v = cerberus.Validator()
    v.validate(c, base_schema)

    return v.errors
