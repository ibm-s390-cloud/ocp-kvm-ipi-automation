#!/usr/bin/python
# -*- coding: utf-8 -*-


DOCUMENTATION = r'''
---
module: crypto_adapter
short_description: Manage crypto adapters.
description:
    - This module configures crypto adapters on s390x hosts.
version_added: "1.0"
options:
    adapter:
        description:
            - The crypto adapter to be configured / deconfigured / enabled / disabled.
            - Must be specified fully qualified using the following notation: '<CARD>.<DOMAIN>'.
        required: true
        default: null
    state:
        description:
            - The desired state of the crypto adapter on the s390x host.
        choices: [ "configured", "deconfigured", "enabled", "disabled" ]
        default: "enabled"
    driver:
        description:
            - The device driver the crypto adapter on the s390x host will be assigned to.
        choices: [ "zcrypt", "other" ]
        default "zcrypt"
notes: []
requirements: []
'''

EXAMPLES = r'''
# configure crypto adapter
- crypto_adapter:
    adapter: '07.0029'
    state: configured

# enable crypto adapter
- crypto_adapter:
    adapter: '07.0029'
    state: enabled

# disable crypto adapter
- crypto_adapter:
    adapter: '07.0029'
    state: disabled

# deconfigure crypto adapter
- crypto_adapter:
    adapter: '07.0029'
    state: deconfigured

# change driver for crypto adapter to 'other'
- crypto_adapter:
    adapter: '07.0029'
    driver: other

# change driver for crypto adapter to 'zcrypt'
- crypto_adapter:
    adapter: '07.0029'
    driver: zcrypt
'''


from enum import Enum
from ansible.module_utils.basic import AnsibleModule


class CryptoAdapterModule(object):

    AdapterDetails = Enum('AdapterDetails', ['ADAPTER', 'TYPE', 'MODE', 'STATUS', 'REQUESTS', 'PENDING', 'HWTYPE', 'QDEPTH', 'FUNCTIONS', 'DRIVER'], start=0)

    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.chzcrypt_cmd = self.module.get_bin_path('chzcrypt', required=True)
        self.lszcrypt_cmd = self.module.get_bin_path('lszcrypt', required=True)

        self.changed = False

        self.process()

    def process(self):
        adapter_device = self.args['adapter']
        target_state = self.args['state']
        target_driver = self.args['driver']

        self._toggle_adapter_state(adapter_device, target_state)
        self._toggle_adapter_driver(adapter_device, target_driver)


    def _toggle_adapter_state(self, target_adapter, target_state):
        current_state = self._get_adapter_detail(target_adapter, CryptoAdapterModule.AdapterDetails.STATUS.value)

        # supported state transitions:
        # deconfig -> configured
        # online -> offline, deconfig
        # offline -> online, deconfig

        if current_state == 'deconfig':
            if target_state == 'configured':
                self._change_adapter_state(target_adapter, target_state)
                self.changed = True
            if target_state == 'deconfigured':
                self.changed = False
            if target_state in ['enabled', 'disabled']:

                # unsupported, critical
                self.module.fail_json('Wrong crypto adapter state: {} is {}'.format(target_adapter, current_state))
        elif current_state == 'online':
            if target_state == 'configured':

                # unsupported but not critical, simply do nothing
                self.changed = False
            if target_state == 'deconfigured':
                self._change_adapter_state(target_adapter, target_state)
                self.changed = True
            if target_state == 'enabled':
                self.changed = False
            if target_state == 'disabled':
                self._change_adapter_state(target_adapter, target_state)
                self.changed = True
        elif current_state == 'offline' :
            if target_state == 'configured':

                # unsupported but not critical, simply do nothing
                self.changed = False
            if target_state == 'deconfigured':
                self._change_adapter_state(target_adapter, target_state)
                self.changed = True
            if target_state == 'enabled':
                self._change_adapter_state(target_adapter, target_state)
                self.changed = True
            if target_state == 'disabled':
                self.changed = False
        else:
            self.module.fail_json('Unknown crypto adapter state: {} is {}'.format(target_adapter, current_state))


    def _toggle_adapter_driver(self, target_adapter, target_driver):
        current_driver = self._get_adapter_detail(target_adapter, CryptoAdapterModule.AdapterDetails.DRIVER.value)

        # driver mapping:
        # zcrypt -> cex*
        # other -> -no-driver-

        # supported driver transitions:
        # cex* -> -no-driver-
        # -no-driver- -> cex*

        if current_driver.startswith('cex'):
            if target_driver == 'zcrypt':
                self.changed = False
            else:
                self._change_adapter_driver(target_adapter, target_driver, '-')
                self.changed = True
        elif 'no-driver' in current_driver:
            if target_driver == 'zcrypt':
                self._change_adapter_driver(target_adapter, target_driver, '+')
                self.changed = True
            else:
                self.changed = False
        else:
            self.module.fail_json('Unknown crypto adapter driver: {} is {}'.format(target_adapter, current_driver))


    def _change_adapter_state(self, adapter, target_state):
        try:
            if target_state == 'configured':
                change_cmd = '{} --config-on {}'.format(self.chzcrypt_cmd, adapter)
            if target_state == 'deconfigured':
                change_cmd = '{} --config-off {}'.format(self.chzcrypt_cmd, adapter)
            if target_state == 'enabled':
                change_cmd = '{} -e {}'.format(self.chzcrypt_cmd, adapter)
            if target_state == 'disabled':
                change_cmd = '{} -d {}'.format(self.chzcrypt_cmd, adapter)

            rc, out, err = self.module.run_command(change_cmd)

            if rc != 0:
                raise Exception('{}, {}, {}'.format(rc, out, err))
        except Exception:
            self.module.fail_json('Unable to change state of crypto adapter: {} to {}'.format(adapter, target_state))


    def _change_adapter_driver(self, adapter, target_driver, bitmode):
        try:
            card = adapter.split('.')[0]
            domain = adapter.split('.')[1]

            change_cmds = {}

            # change the crypto adapter card driver assignment
            card_cmd = 'echo {}{} > /sys/bus/ap/apmask'.format(bitmode, int(card))
            change_cmds['card'] = card_cmd

            # change the crypto adapter domain assignment
            domain_cmd = 'echo {}{} > /sys/bus/ap/aqmask'.format(bitmode, int(domain))
            change_cmds['domain'] = domain_cmd

            for k, v in change_cmds.items():
                rc, _, _ = self.module.run_command(v, use_unsafe_shell=True)

                if rc != 0:
                    raise Exception('Unable to change driver of crypto adapter {}: {} to {}'.format(k, adapter, target_driver))
        except Exception as e:
            self.module.fail_json(e)


    def _get_adapter_detail(self, target_adapter, detail_index):
        adapter_detail = None

        try:
            adapter_detail = ''
            adapter_info = self._get_adapter_info(target_adapter)

            adapter_detail = adapter_info[detail_index]

            if not adapter_detail:
                raise Exception
        except Exception:
            self.module.fail_json('Unable to determine crypto adapter detail: {}'.format(target_adapter))

        return adapter_detail


    def _get_adapter_info(self, target_adapter):
        adapter_info = []

        list_cmd = '{} -V'.format(self.lszcrypt_cmd)

        rc, out, err = self.module.run_command(list_cmd)

        if rc != 0:
            self.module.fail_json('Unable to determine crypto adapter info: {}'.format(target_adapter))
        else:
            try:
                out_lines = out.split("\n")

                # skip the first two lines of the 'lszcrypt' output
                i = 2

                while i < len(out_lines):
                    a = out_lines[i].split()

                    if a[0] == target_adapter:
                        adapter_info = a
                        break

                    i+=1

                # raise an exception if the target adapter could not be found
                if not adapter_info:
                    raise Exception
            except Exception:
                self.module.fail_json('Unable to determine crypto adapter info: {}'.format(target_adapter))

        return adapter_info


def main():
    module = AnsibleModule(
        argument_spec = dict(
            adapter = dict(type='str', required=True),
            state = dict(type='str', default='enabled', choices=['configured', 'deconfigured', 'enabled', 'disabled'], required=False),
            driver = dict(type='str', default='zcrypt', choices=['zcrypt', 'other'], required=False),
        ),
        supports_check_mode=True
    )

    result = CryptoAdapterModule(module)

    module.exit_json(changed=result.changed)


if __name__ == '__main__':
    main()
