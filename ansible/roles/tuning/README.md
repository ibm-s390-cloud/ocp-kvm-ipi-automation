# KVM-based OpenShift cluster tuning

The Ansible role in this directory is used in conjunction with the `tune_ocp_install.yml` auxiliary Ansible playbook.

## How to run it

To run the cluster tuning playbook simply issue the following commands:

```bash
cd ansible
ansible-playbook -i inventory tune_ocp_install.yml
```

## What it does

The cluster tuning playbook (and by proxy the role) tunes various aspects of the KVM guest configuration and the in-cluster worker node configuration. It implements some of the tuning guidelines from the following sources:

- <https://docs.openshift.com/container-platform/4.8/scalability_and_performance/ibm-z-recommended-host-practices.html#ibm-z-rhel-kvm-host-recommendations_ibm-z-recommended-host-practices>
- <https://www.ibm.com/docs/en/linux-on-systems?topic=cpus-virtual-cpu-tuning>
- <https://public.dhe.ibm.com/software/dw/linux390/perf/OpenShift_on_IBM_Z_-_Performance_Experiences_V11.pdf>
- <https://developer.ibm.com/tutorials/red-hat-openshift-on-ibm-z-tune-your-network-performance-with-rfs/>

In order to change the various configuration parameters of the cluster nodes, the playbook is divided into two distinct phases and the corresponding subsequent actions:

- OpenShift cluster is (temporarily) offline:
  - optimize libvirt network used by OpenShift cluster
  - disable 'memballoon' device for all cluster nodes
  - add dedicated IO threads for disk access to all cluster nodes
  - assign root disk to dedicated IO thread for all cluster nodes
  - increase the CPU weight (shares) for all cluster worker nodes

- OpenShift cluster is online:
  - enable 'receive flow steering' network setting for all cluster worker nodes
  - disable transparent huge pages for all cluster worker nodes

At the end of the successful cluster tuning process, the OpenShift cluster is online and fully operational. The result of the cluster tuning process is documented *within* the cluster itself, using an annotation field in the `ClusterVersion` object's metadata:

```bash
> oc get clusterversion -o yaml

apiVersion: v1
items:
- apiVersion: config.openshift.io/v1
  kind: ClusterVersion
  metadata:
    annotations:
      kvm-ipi-automation-tuned: "true"
    creationTimestamp: "2022-01-11T10:31:30Z"
    generation: 2
    name: version
    resourceVersion: "42021"
    uid: f9d5b816-c9ed-4c89-8577-c0718bffeb1a
  spec:
  ...
```
