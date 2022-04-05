# FAQ

## Introduction

In this document you'll find a list of the most frequently asked questions concerning the playbooks in this repository as well as more generic Red Hat OpenShift Container Platform topics.

## Q: I have an air-gapped target LPAR / KVM host - can I do an offline OCP installation with these playbooks?

A: **No**, the playbooks in this repository do rely on the target LPAR / KVM host to be connected to the network with unrestricted access to the internet. This is needed in order to pull the OCP installation artifacts from the official Red Hat servers.

## Q: Can I install / run multiple OCP clusters on the same target LPAR / KVM host with these playbooks?

A: **No**, multiple OCP clusters on the same host are not supported by these playbooks. Please see also the included [documentation](DOCUMENTATION.md) for details.

## Q: Can I install an OCP cluster that spans multiple KVM hosts with these playbooks?

A: **No**, this kind of OCP cluster topology is not supported by the Red Hat Openshift installer when using libvirt and IPI. So by extension these playbooks do not support it either.

## Q: I understand that the OCP cluster will be using a virtual bridge and NAT to connect to the network and gain access to the internet. Can I change this and use a different type of networking setup, e.g. macvtap or openvswitch?

A: **No**, using a virtual bridge and NAT is the only networking option provided by the Red Hat Openshift installer when using libvirt and IPI. If you have the need for a different type of network setup for your prospective OCP cluster you have to use UPI instead. Please refer to <https://github.com/IBM/Ansible-OpenShift-Provisioning> for an alternative solution to install OCP on your KVM host using UPI.

## Q: IPI? UPI? What does that mean? What's the significance?

A: OCP can be installed on a variety of platforms and server architectures. In order to support these, the OpenShift installer implements two different strategies for installing OCP: either via 'user-provisioned infrastructure' (UPI) or 'installer-provisioned infrastructure' (IPI). With UPI, the user who wants to install OCP must make sure that all the required hardware and software resources (e.g. bare metal servers / virtual machines, static network addresses) that make up the individual parts of the OCP cluster are present and accounted for before the actual OCP installation takes place. Hence, this strategy requires a substantial amount of advance planning as well as a fairly good knowledge of the underlying platform / server architecture and the topology of the prospective OCP cluster that is to be installed on top of it. With IPI, however, the OpenShift installer itself creates the required cluster resources to be able to establish the final OCP cluster, thus relieving the user from having to gather all the resources and information beforehand and making the OCP installation a less involved process. The playbooks in this repository are implemented aroung the 'IPI' OCP installation strategy.

## Q: My target LPAR / KVM host that's running my OCP cluster needs to be rebooted. Does the OCP cluster survive this / still work after the reboot is done?

A: **Yes**, the OCP cluster will survive the host reboot. You just have to make sure that the cluster gets started by starting the virtual machines (libvirt domains) that make up the individual cluster nodes on the host. It is recommended to use the playbook 'start_ocp_cluster_nodes.yml' included in this repository for this purpose:

```bash
cd ansible

# start the cluster nodes and wait for the OCP cluster to come online
ansible-playbook -i inventory start_ocp_cluster_nodes.yml

# check the OCP cluster for health issues (e.g. alerts)
ansible-playbook -i inventory check_ocp_cluster_state.yml
```

## Q: I am frequently setting up / tearing down OCP clusters. My OpenShift Cluster Manager (OCM) instance is littered with references to stale clusters that no longer exist. How do I get rid of these?

A: Deleting clusters in state 'stale' in OCM is not possible at the moment. That said, there is a way to _archive_ stale clusters meaning moving them out of OCM's main view into a separate view called 'cluster archives'. Follow these steps to do that for your OCM instance:

- download the latest `ocm` CLI binary to your Ansible workstation (see: <https://github.com/openshift-online/ocm-cli/releases>)
- fetch your personal OCM API token from <https://console.redhat.com/openshift/token>
- login to OCM via `ocm login --token=<your_api_token>`
- run this shell script to archive all existing stale OCP clusters:
  
  ```bash
  #/usr/bin/env bash

  # create temporary OCM request payload file
  cat <<EOF > sub.json
  {
    "status": "Archived"
  }
  EOF

  # get all stale clusters from OCM and patch them with status 'Archived'
  for i in $(ocm get /api/accounts_mgmt/v1/subscriptions --parameter size=1000 --parameter search="status in ('Stale')" | jq  -r ".items[].id"); do
    ocm patch "/api/accounts_mgmt/v1/subscriptions/$i" --body 'sub.json'
  done
  ```

You can also enable OCM integration with the playbooks in this repository so that whenever you delete an existing cluster via the `cleanup_ocp_install.yml` playbook it will be acrhived in OCM automatically. For details on how to enable this integration please see [here](../ansible/secrets/README.md).
