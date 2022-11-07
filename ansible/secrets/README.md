# The purpose of this directory

This directory is solely used to *temporarily* store secrets that are used to install / manage an OpenShift cluster using IPI (installer-provisioned infrastructure) on a KVM host.

These secrets are:

- `.ocp4_pull_secret` - RHOCP image pull secret file, required
- `.ocm_api_token` - OCM API token, optional

## .ocp4_pull_secret

Before you can use any of the Ansible playbooks in this repository you need to fetch this file from Red Hat and put it into this directory. Make sure the file is named `.ocp4_pull_secret` (hidden file, no extension) so that the Ansible playbooks will pick it up. If the file is missing or not named properly, the Ansible playbooks will fail to run (no worries, the playbooks have a soundness check implemented that will look for the image pull secret file before anything is done actually).

## .ocm_api_token

The Red Hat OpenShift Cluster Manager (OCM) is a portal that keeps track of all RHOCP cluster installations for a given Red Hat account / user ID. Upon deletion of an existing cluster on the target KVM host the information for that cluster can be archived in the OCM inventory, essentially marking a cluster as no longer subscribed / used. The `cleanup_ocp_install.yml` playbook can do that for you automatically, you just need to put a file named `.ocm_api_token` (hidden file, no extension) containing the OCM API token (see also: <https://console.redhat.com/openshift/token>) in this folder. OCM integration is completely optional, depending on the presence of `.ocm_api_token`.

The `.gitignore` file in this directory will ensure that whatever you place in here will not be persisted in git.
