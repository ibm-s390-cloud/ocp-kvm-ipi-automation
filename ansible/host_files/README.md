# The purpose of this directory

This directory is used to store auxiliary files that are of importance to the OpenShift cluster installation process:

- *advanced* cluster configuration files
- user-provided Ansible playbooks

The `.gitignore` file in this directory will ensure that whatever you place in here will not be persisted in git.

## Advanced cluster configuration files

The OpenShift cluster installation process supports the inclusion of *advanced* cluster configuration files. These files are:

- `cluster-network-03-config.yml` - OpenShift cluster network configuration file (see: <https://docs.openshift.com/container-platform/4.12/installing/installing_bare_metal/installing-bare-metal-network-customizations.html>)

The cluster configuration files **must** be organized by KVM hosts, meaning that for every KVM host a specific configuration should be applied to a dedicated subdirectory must exist within this directory.

For example:

```bash
/ansible
...
├── host_files
│   ├── <my_kvm_host_name_1>
│   │   └── cluster-network-03-config.yml
│   └── <my_kvm_host_name_2>
│       └── cluster-network-03-config.yml
...
```

## User-provided Ansible playbooks

- `post_boot_tasks.yml` - a simple Ansible playbook containing one or more tasks to do whatever is needed for a given target host as part of a post-boot customization process

The user-provided Ansible playbooks **must** be organized by KVM hosts, meaning that for every KVM host a specific post-boot customization process should be applied to a dedicated subdirectory must exist within this directory.

For example:

```bash
/ansible
...
├── host_files
│   ├── <my_kvm_host_name_1>
│   │   └── post_boot_tasks.yml
│   └── <my_kvm_host_name_2>
│       └── post_boot_tasks.yml
...
```

The Ansible playbook provided by the user should contain only simple tasks (e.g. `ansible.builtin.shell` or `ansible.builtin.command`). If any of the tasks contained in the user-provided playbook fails the entire playbook run (e.g. `setup_host.yml`) will fail.

Here's an example of a simple `post_boot_tasks.yml` playbook for an IBM zSystems / LinuxONE target host that activates a DASD disk and mounts the filesystem contained on that disk accordingly:

```yaml
---

- name: attach DASD disks to host
  ansible.builtin.shell: |
    cio_ignore -r 0.0.{{ item.disk_id }}
    chccwdev -e 0.0.{{ item.disk_id }}
    mount {{ item.device_id }} {{ item.mount_point }}
  loop:
    - { 'disk_id': 'b7a0', 'device_id': '/dev/dasdb1', 'mount_point': '/var/lib/libvirt/openshift-images' }
```
