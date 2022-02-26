# Troubleshooting

## Introduction

While the playbooks in this repository have been used successfully many times on a wide variety of target KVM hosts there's still the off chance that you'll run into issues occasionally.

Please see the issues / problems described in this document to see if anything matches your specific use case.

## Missing Ansible collection

When running one of the playbooks in this repository you might be presented with an Ansible error message similar to the following:

```text
ERROR! couldn't resolve module/action 'community.general.ansible_galaxy_install'. This often indicates a misspelling, missing collection, or incorrect module path.
...
```

As the error message indicates this is caused by a missing (or outdated) Ansible collection required by the playbooks. You can fix the issue by installing / updating all Ansible collections using the following command:

```bash
cd ansible
ansible-galaxy collection install -r requirements.yml --force
```

Please note that it is very likely for the `requirements.yml` file to be updated on a regular basis as the playbooks in this repository will be enhanced over time. Therefore it is probably a good idea to always update the Ansible collections *after* you've pulled a new version of the `ocp-kvm-ipi-automation` GitHub repository.

## The OCP cluster installation task times out

If you get timeouts from one of the following OCP cluster installation tasks:

- 'wait until libvirt cluster network has been created' (playbook: 'run_ocp_install.yml')
- 'wait until cluster installation has finished' (playbook: 'run_ocp_install.yml')

it is most likely due to an issue with the OpenShift installer process that is run on the target KVM host. There's actually quite a few things that can go wrong during the OCP cluster installation process - the following sections describe the *known* issues that have been observed so far.

Debugging the OCP installation process can be daunting task and requires some knowledge about OpenShift and libvirt / KVM in general. As a starting point it's best to observe the OCP installation process on the target KVM host by looking at the cluster installation log file:

```bash
# login to the target KVM host via SSH
ssh root@$$YOUR_KVM_HOST_NAME$$

# observe the OCP cluster installation log file
tail -fn +1 /root/ocp4-workdir/.openshift_install.log
```

### Using an incompatible libvirt version

The OCP cluster installation times out and you'll find this error message in the OCP cluster installation log file:

```text
FATAL failed to initialize the cluster: Some cluster operators are still updating: authentication, console, image-registry, ingress, monitoring
```

When taking a look at the cluster's Machine resources you'll see that all Machines representing cluster worker nodes are in state `Provisioning`:

```bash
# login to the target KVM host via SSH
ssh root@$$YOUR_KVM_HOST_NAME$$

# get details about the cluster's Machine resources
KUBECONFIG=/root/ocp4-workdir/auth/kubeconfig oc get machines --all-namespaces
...
NAMESPACE               NAME                         PHASE          TYPE   REGION   ZONE   AGE
openshift-machine-api   test1-xpjr5-master-0         Running                               49m
openshift-machine-api   test1-xpjr5-master-1         Running                               49m
openshift-machine-api   test1-xpjr5-master-2         Running                               49m
openshift-machine-api   test1-xpjr5-worker-0-5z7mt   Provisioning                          46m
openshift-machine-api   test1-xpjr5-worker-0-bm4cl   Provisioning                          46m
openshift-machine-api   test1-xpjr5-worker-0-bqhng   Provisioning                          46m
```

This issue is caused by incompatible libvirt packages installed on your KVM host, making it impossible for the OpenShift installer to modify the libvirt network of the OCP cluster during the installation process.

To resolve this problem make sure to downgrade all libvirt packages on your KVM host to a working version like this:

```bash
# login to the target KVM host via SSH
ssh root@$$YOUR_KVM_HOST_NAME$$

# downgrade all libvirt packages
yum downgrade -y libvirt
```

Afterwards run the following playbooks in this repository to reboot the KVM host and cleanup the failed OCP cluster installation:

```bash
cd ansible
ansible-playbook reboot_host.yml
ansible-playbook ansible-playbook cleanup_ocp_install.yml -e cleanup_ignore_errors=true
```

Please note that the playbooks do implement a safeguard mechanism to ensure that under normal circumstances this libvirt incompatibility issue will not manifest itself. However depending on your actual KVM host configuration there's still the off chance for this to happen, hence it being mentioned here.

### General OCP cluster bootstrapping issues

The OCP cluster installation times out and you'll find an error message in the OCP cluster installation log file similar to this:

```text
time="2022-02-23T09:11:17+01:00" level=debug msg="Still waiting for the Kubernetes API: Get \"https://api.perfocs1.lnxperf.boe:6443/version?timeout=32s\": dial tcp 192.168.126.13:6443: connect: connection refused"
```

When taking a look at the libvirt domains running on the KVM host you'll see that all cluster worker nodes are missing and only the master nodes and the bootstrap node are present:

```bash
# login to the target KVM host via SSH
ssh root@$$YOUR_KVM_HOST_NAME$$

# list all libvirt domains
virsh list --all
...
 Id   Name                       State
------------------------------------------
 1    perfocs1-mwxkx-master-1    running
 2    perfocs1-mwxkx-master-0    running
 3    perfocs1-mwxkx-bootstrap   running
 4    perfocs1-mwxkx-master-2    running
```

This usually indicates that the OCP cluster bootstrapping process has failed. You can try to find out as to what happened and why by logging into the bootstrap node and taking a look at the bootstrap logs:

```bash
# login to the target KVM host via SSH
ssh root@$$YOUR_KVM_HOST_NAME$$

# login to the bootstrap node via SSH (note: the IP address of the bootstrap node is always 192.168.126.10)
ssh -i /root/ocp4-workdir/id_ssh_ocp core@192.168.126.10

# display bootstrap logs
journalctl -b -f -u bootkube.service
```

The bootstrap logs hopefully will give you some hint on what went wrong and how to resolve the issue.
