#!/usr/bin/python
# -*- coding: utf-8 -*-


DOCUMENTATION = r'''
---
module: mdev_uuid_gen
short_description: Generates UUIDs to be used by mediated devices.
description:
    - This module generates UUIDs to be used by mediated devices on s390x hosts.
version_added: "1.0"
options:
    worker_index:
        description:
            - The numeric index of the libvirt domain (zero-based).
        required: true
        default: null
    resource_assignments:
        description:
            - The crypto resource assignment matrix.
        required: true
        default: null
notes: []
requirements: []
'''

RETURN = r'''
mdev_uuids:
    description: Dictionary containing the mediated device UUIDs.
    returned: success
    type: dictionary
    contains:
        <uuid>:
            description: Key-value pair containing a UUID (key) and the corresponding crypto resource (value)
            returned: success
            type: string
            sample: '34EF0DE3-AB1C-4ADC-AC6C-0741338B39EA:07.0029'
'''

EXAMPLES = r'''
# generate
mdev_uuid_gen:
  worker_index: 0
  resource_assignments:
    - id: '07.0029'
      assign_to_worker: 0
    - id: '07.002a'
      assign_to_worker: 1
    - id: '07.002b'
      assign_to_worker: 2
'''


import uuid
from ansible.module_utils.basic import AnsibleModule


class MdevUuidGenModule(object):
    def __init__(self, module):
        self.module = module
        self.args = self.module.params

        self.changed = True
        self.mdev_uuids = []

        self.process()

    def process(self):
        worker_index = self.args['worker_index']
        resource_assignments = self.args['resource_assignments']

        self.mdev_uuids = self._generate_mdev_uuids(worker_index, resource_assignments)

    def _generate_mdev_uuids(self, worker_index, resource_assignments):
        uuid_resource_mapping = {}

        # iterate over list of resource-to-worker assignments
        for a in resource_assignments:

            # a has two keys-value pairs:
            # - id: the fully qualified crypto resource id
            # - assign_to_worker: the numeric index of the worker the crypto resource is to be assigned to
            if a['assign_to_worker'] != worker_index:

                # skip all items where the assigned worker does not match the given worker index
                continue

            # generate random UUID
            resource_uuid = uuid.uuid4()

            # store UUID to crypto resource mapping information for the given worker
            uuid_resource_mapping[str(resource_uuid)] = a['id']

        return uuid_resource_mapping


def main():
    module = AnsibleModule(
        argument_spec = dict(
            worker_index = dict(type='int', required=True),
            resource_assignments = dict(type='list', required=True),
        ),
        supports_check_mode=True
    )

    result = MdevUuidGenModule(module)

    module.exit_json(mdev_uuids=result.mdev_uuids, changed=result.changed)


if __name__ == '__main__':
    main()
