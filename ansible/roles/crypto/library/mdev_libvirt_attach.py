#!/usr/bin/python
# -*- coding: utf-8 -*-


DOCUMENTATION = r'''
---
module: mdev_libvirt_attach
short_description: Attach mediated devices to libvirt domains.
description:
    - This module attaches mediated devices to libvirt domains on s390x hosts.
version_added: "1.0"
options:
    device_index:
        description:
            - The numeric index of the mediated device (zero-based).
        required: true
        default: null
    device_uuid:
        description:
            - The UUID of the mediated device.
        required: true
        default: null
    worker_name:
        description:
            - The name of the libvirt domain to attach the mediated device to.
        required: true
        default: null
notes:
    - Supports attaching multiple mediated devices to a libvirt domain although this is yet to supported by libvirt itself.
requirements: []
'''

EXAMPLES = r'''
# attach a mediated device
mdev_libvirt_attach:
  device_index: 0
  device_uuid: '34EF0DE3-AB1C-4ADC-AC6C-0741338B39EA'
  worker_name: 'ocp1-qf2b5-worker-0-456r9'
'''


import os
import tempfile
from ansible.module_utils.basic import AnsibleModule


MEDIATED_DEVICE_XML_TEMPLATE = '''
<hostdev mode='subsystem' type='mdev' managed='no' model='vfio-ap'>
  <source>
    <address uuid='{}'/>
  </source>
  <alias name='hostdev{}'/>
</hostdev>
'''


class MdevLibvirtAttachModule(object):
    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.virsh_cmd = self.module.get_bin_path('virsh', required=True)

        self.changed = True

        self.process()

    def process(self):
        device_index = self.args['device_index']
        device_uuid = self.args['device_uuid']
        worker_name = self.args['worker_name']

        self.mdev_uuids = self._attach_device(device_index, device_uuid, worker_name)

    def _attach_device(self, device_index, device_uuid, worker_name):
        device_xml = MEDIATED_DEVICE_XML_TEMPLATE.format(device_uuid, device_index)
        temp_xml = None
        rc = 0

        try:

            # save the XML to a temporary named file
            temp_xml = tempfile.NamedTemporaryFile(mode='w+t', suffix='.xml', delete=False)
            temp_xml.write(device_xml)
            temp_xml.flush()
            temp_xml.close()

            attach_cmd = '{} attach-device --domain {} --file {} --config '.format(self.virsh_cmd, worker_name, temp_xml.name)

            rc, _, _ = self.module.run_command(attach_cmd)
        finally:
            if temp_xml:
                os.unlink(temp_xml.name)

        if rc != 0:
            self.module.fail_json('Unable to attach mediated device {} to worker {}'.format(device_uuid, worker_name))


def main():
    module = AnsibleModule(
        argument_spec = dict(
            device_index = dict(type='int', required=True),
            device_uuid = dict(type='str', required=True),
            worker_name = dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    result = MdevLibvirtAttachModule(module)

    module.exit_json(changed=result.changed)


if __name__ == '__main__':
    main()
