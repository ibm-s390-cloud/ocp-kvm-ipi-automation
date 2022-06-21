# The purpose of this directory

This directory is used to store *advanced* cluster configuration files that are of importance to the OpenShift cluster installation process.

These cluster configuration files are:

- `cluster-network-03-config.yml` - OpenShift cluster network configuration file (see: <https://docs.openshift.com/container-platform/4.10/installing/installing_bare_metal/installing-bare-metal-network-customizations.html>)

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

The `.gitignore` file in this directory will ensure that whatever you place in here will not be persisted in git.
