# The purpose of this directory

This directory is solely used to *temporarily* store the image pull secret file that is required to install an OpenShift cluster using IPI (installer-provisioned infrastructure) on a KVM host.

Before you can use any of the Ansible playbooks in this repository you need to fetch this file from Red Hat and put it into this directory. Make sure the file is named `.ocp4_pull_secret` (hidden file, no extension) so that the Ansible playbooks will pick it up. If the file is missing or not named properly, the Ansible playbooks will fail to run (no worries, the playbooks have a sanity check implemented that will look for the image pull secret file before anything is done actually).

The `.gitignore` file in this directory will ensure that whatever you place in here will not be persisted in git.
