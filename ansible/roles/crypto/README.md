# Enabling crypto resource support

The Ansible role in this directory is used in conjunction with the `enable_crypto_resources.yml` auxiliary Ansible playbook.

## How to configure it

Assignment of the crypto resources available on the KVM host to individual cluster worker nodes can be configured in the host-specific '$$YOUR_KVM_HOST_NAME$$.yml' configuration file. The following properties in that file determine how the crypto resources will be exposed to the cluster:

```yaml
# a list of crypto resources present on the host that are to be exposed
# to the OpenShift cluster worker nodes (using the k8s CEX device plugin)
# (see also: https://github.com/ibm-s390-cloud/k8s-cex-dev-plugin)
crypto_adapters:
  - id: '07.0029'              # crypto resource identifier in <adapter>.<domain> format using **hexadecimal** values
    assign_to_worker: 0        # cluster worker node index (indexing start at zero)
  - id: '07.002a'
    assign_to_worker: 1
  - id: '07.002b'
    assign_to_worker: 2

# the name of the CryptoConfigSet project into which all crypto resources will be put
crypto_config_set_project: kvm-ipi-automation
```

As you can see every resource that is to be used needs to be explicitely listed as a member of the  `crypto_adapter` array. The `id` field of the crypto resource needs to be fully qualified (meaning a combination of crypto adapter and crypto domain) and corresponds to the output given by the OS-level command `lszcrypt -V` run on the KVM host. The `assign_to_worker` field determines which cluster worker node the crypto resource will be attached to (the value actually denotes a worker node index).

Please be aware that due to a current limitation of libvirt **only one crypto resource per worker node** is allowed. Upon running the playbook the given `crypto_adapters` configuration settings will be sanity-checked for validity.

## How to run it

To run the crypto resource enablement playbook simply issue the following commands:

```bash
cd ansible
ansible-playbook -i inventory enable_crypto_resources.yml
```

## What it does

The crypto resources enablement tuning playbook (and by proxy the role) exposes crypto resources (adapters and domains) present on the KVM host to the OpenShift cluster worker nodes so that crypto-enabled containerized workloads can make use of it. The usage of crypto resources within the cluster is facilitated by the Kubernetes CEX device plugin available [here](https://github.com/ibm-s390-cloud/k8s-cex-dev-plugin).

Before the plugin can be installed however plenty of configuration modifications need to be made for the KVM host itself as well as the KVM guests that make up the OpenShift cluster worker nodes. The playbook takes care of all of this:

- load the required kernel modules on the KVM host
- generate mediated devices for all crypto resources that are to be exposed to KVM guests
- record the UUIDs of these mediated devices and the corresponding mapping to KVM guests
- install a libvirt lifecycle hook that takes care of creating / destroying mediated devices based on the recorded information to enable KVM guest **and** KVM host restarts
- modify cluster worker node KVM guests to attach mediated devices
- create a cex-resources-config ConfigMap resource within the OpenShift cluster to announce available crypto resources to the cluster
- install the Kubernetes CEX device plugin as a DaemonSet resource within the OpenShift cluster to allow access by containerized workloads

At the end of the successful crypto resource enablement process, the OpenShift cluster is online and fully operational, with crypto-enabled workloads ready to start utilizing the crypto resources. Out of the box, all crypto resources configured by the user will be put into a single CryptoConfigSet resource, e.g.:

```json
{
    "cryptoconfigsets":
    [
        {
            "setname": "ocp1-vbtmg",
            "project": "kvm-ipi-automation",
            "cexmode": "ep11",
            "apqns":
            [
                {
                    "adapter": 7,
                    "domain": 41,
                    "machineid": ""
                },
                {
                    "adapter": 7,
                    "domain": 42,
                    "machineid": ""
                },
                {
                    "adapter": 7,
                    "domain": 43,
                    "machineid": ""
                }
            ]
        }
    ]
}
```

The `setname` property will always reflect the internal cluster ID of the OpenShift cluster that is created by the OpenShift installer during the cluster installation phase. The `project` property per default is set to 'kvm-ipi-automation' but this can be overridden by the user via the host.yml template file.

## Optional: installing the EP11 binaries on the KVM host

The crypto resources enablement tuning playbook allows you to automatically install the EP11 binaries on the KVM host. As these binaries are not part of the underlying RHEL 8.x distribution but need to be downloaded separately from IBM this installation step is completely optional and will be skipped if the binaries are not provided by the user. The most recent EP11 binaries (available as RPM or Debian packages) can be obtained from this website: <https://www.ibm.com/resources/mrs/assets?source=ibmzep11>.

Make sure to download at least the following files:

- ep11-host-\<version\>.s390x.rpm
- ep11-host-devel-\<version\>.s390x.rpm

In order for the playbook to pick up these files and install them on the KVM host you need to put them into the following folder in this repository: `${repository_root}/ansible/roles/crypto/files/ep11`. No worries, these files won't get persisted in git / GHE as the `.gitignore` file in that folder explicitely excludes these files.

After you have put the EP11 RPM packages in the correct folder, simply run the `enable_crypto_resources.yml` playbook as shown above and the EP11 binaries will be installed on the KVM host as part of the crypto resource enablement process.
