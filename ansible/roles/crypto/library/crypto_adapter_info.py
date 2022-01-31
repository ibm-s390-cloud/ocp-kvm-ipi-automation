#!/usr/bin/python
# -*- coding: utf-8 -*-


DOCUMENTATION = r'''
---
module: crypto_adapter_info
short_description: Get details of a given crypto adapter.
description:
    - This module fetches the details of a given crypto adapter from s390x hosts.
version_added: "1.0"
options:
    adapter:
        description:
            - The ID of the crypto adapter to be queried for detailed information.
            - This ID can either be a crypto adapter card number, e.g. '07'
            - or a crypto adapter domain number, e.g. '07.0029'.
        required: true
        default: null
notes: []
requirements: []
'''

EXAMPLES = r'''
# get information for crypto adapter card
- crypto_adapter_info:
    adapter: '07'

# get information for crypto adapter domain
- crypto_adapter_info:
    adapter: '07.0029'
'''

RETURN = r'''
adapter_info:
    description: Dictionary containing the crypto adapter information.
    returned: success
    type: dictionary
    contains:
        card:
            description: The crypto adapter ID.
            returned: success
            type: string
            sample: '07'
        type:
            description: The crypto adapter type.
            returned: success
            type: string
            sample: 'CEX6P'
        mode:
            description: The crypto adapter mode of operation.
            returned: success
            type: string
            sample: 'EP11-Coproc'
        status:
            description: The crypto adapter status.
            returned: success
            type: string
            sample: 'online'
        requests:
            description: The number of requests made to the crypto adapter.
            returned: success
            type: string
            sample: '0'
        pending:
            description: The number of requests made to the crypto adapter that are pending.
            returned: success
            type: string
            sample: '0'
        hwtype:
            description: The hardware type of the crypto adapter.
            returned: success
            type: string
            sample: '12'
        qdepth:
            description: The crypto adapter queue depth.
            returned: success
            type: string
            sample: '08'
        functions:
            description: The configured functions of the crypto adapter.
            returned: success
            type: string
            sample: '-----XNF-'
        driver:
            description: The Linux driver used by the crypto adapter.
            returned: success
            type: string
            sample: 'cex4card'
'''


from ansible.module_utils.basic import AnsibleModule


class CryptoAdapterInfoModule(object):
    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.lszcrypt_cmd = self.module.get_bin_path('lszcrypt', required=True)

        self.changed = True
        self.adapter_info = {}

        self.process()


    def process(self):
        adapter_device = self.args['adapter']
        self.adapter_info = self._get_adapter_info(adapter_device)


    def _get_adapter_info(self, target_adapter):
        list_cmd = '{} -V'.format(self.lszcrypt_cmd)

        adapter_info = {}
        rc, out, _ = self.module.run_command(list_cmd)

        if rc != 0:
            return adapter_info
        else:
            out_lines = out.split("\n")

            # skip the first two lines of the 'lszcrypt' output
            i = 2

            while i < len(out_lines):
                a = out_lines[i].split()
                adapter = {
                    'card': a[0],
                    'type': a[1],
                    'mode': a[2],
                    'status': a[3],
                    'requests': a[4],
                    'pending': a[5],
                    'hwtype': a[6],
                    'qdepth': a[7],
                    'functions': a[8],
                    'driver': a[9]
                }

                if adapter["card"] == target_adapter:
                    adapter_info = adapter
                    break

                i = i + 1

            return adapter_info


def main():
    module = AnsibleModule(
        argument_spec = dict(
            adapter = dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    result = CryptoAdapterInfoModule(module)

    module.exit_json(adapter_info=result.adapter_info, changed=result.changed)


if __name__ == '__main__':
    main()
