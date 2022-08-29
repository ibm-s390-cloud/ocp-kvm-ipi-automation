# tekton

This folder contains OpenShift Pipelines (Tekton) resources for various KVM host-related activities, e.g. installing RHOCP, rebooting the host, etc.
Please consider these resources as examples (rather than ready-to-use resources) on how to utilize the Ansible playbooks in this repository from within an existing Red Hat OpenShift cluster that has OpenShift Pipelines (<https://docs.openshift.com/container-platform/4.11/cicd/pipelines/op-release-notes.html>) installed.

## Overview

The following resources are included in this folder:

| Resource type | Name  | Purpose | Details |
|---------------|-------|---------|---------|
| Task | sleep | Generic task that will sleep for a given amount of time | |
| Task | kvm-run-playbook | Run a given ocp-kvm-ipi-automation Ansible playbook against a KVM host | Uses the ocp-kvm-ipi-automation Docker image built by Pipeline 'build-kvm-deployer' |
| Pipeline | build-kvm-deployer | Builds a Docker image for ocp-kvm-ipi-automation (using the Dockerfile in this repository) and stores it in the internal RHOCP image registry | |
| Pipeline | deploy-ocp-kvm-host | Deploy RHOCP on a KVM host | Uses the Task 'kvm-run-playbook' |
| Pipeline | cleanup-kvm-host | Uninstall RHOCP from a KVM host and clean up all remaining artifacts | Uses the Task 'kvm-run-playbook' |
| Pipeline | reboot-kvm-host | Reboot a KVM host | Uses the Task 'kvm-run-playbook' |
| Pipeline | tune-ocp-kvm-host | Tune the existing RHOCP installation on a KVM host | Uses the Task 'kvm-run-playbook' |

## Usage

The resources in this folder rely on a few thinsg that need to be setup before you can actually start using them.

### Secrets

The following secrets need to present at the time before any of the included pipelines and tasks is used:

- name: kvm-deployer-ssh, type: Secret
- name: kvm-deployer-secrets, type: Secret

These secrets can be created by running the following commands:

```bash
# create kvm-deployer-ssh secret
# first create a new SSH keypair and configure your target KVM host's root account to accept it as authorized key
cd $HOME
ssh-keygen -t rsa -f $HOME/.ssh/id_ansible
ssh-copy-id -i $HOME/.ssh/id_ansible root@<YOUR_KVM_HOST_NAME>
# afterwards create the secret containing the SSH keypair
cd $HOME/.ssh
oc project <YOUR_TEKTON_PROJECT>
oc create secret generic kvm-deployer-ssh --from-file=id_ansible=./id_ansible --from-file=id_ansible.pub=./id_ansible.pub

# create kvm-deployer-secrets secret
cd $HOME
# fetch your personal RHOCP image pull secret file from your Red Hat account and put it into $HOME/.ocp4_pull_secret
# afterwards create the secret containing the RHOCP image pull secret
oc project <YOUR_TEKTON_PROJECT>
oc create secret generic kvm-deployer-secrets --from-file=.ocp4_pull_secret=./.ocp4_pull_secret
```

### KVM host configuration files

KVM host configuration for the Pipeline resources must be done via a dedicated GitHub repository. All Pipeline resources make use of workspaces that get populated by fetching files from a remote repository, e.g.:

```yaml
...
  tasks:
  - name: fetch-config
    params:
    - name: url
      value: $(params.configs-url)
    - name: revision
      value: $(params.configs-branch)
    taskRef:
      kind: ClusterTask
      name: git-clone
    workspaces:
    - name: output
      workspace: configs
...
```

For this to work make sure you create a new GitHub repository that is outlined like this:

```bash
.
└── config
    ├── MY_KVM_HOST_1
    │   ├── host_vars
    │   │   └── MY_KVM_HOST_1.yml
    │   ├── inventory
    │   └── ssh_config
    ├── MY_KVM_HOST_2
    │   ├── host_vars
    │   │   └── MY_KVM_HOST_2.yml
    │   ├── inventory
    │   └── ssh_config
    ├── ...
```

You'll recognize the `inventory` files as well as the host-specific configuration YAML files in the `host_vars` subfolders - these are required by the Ansible playbooks. Please refer to the [documentation](../docs/DOCUMENTATION.md) for more details on those files.

The `ssh_config` file is required for the 'kvm-deployer' pod that is part of the pipelines to actually make a SSH connection to the target KVM host to be able to run the Ansible playbooks. Make sure the `ssh_config` file looks like this:

```text
ForwardX11 no
ForwardX11Trusted no
GSSAPIAuthentication no
HashKnownHosts yes

Host *
  ConnectTimeout 90
  IdentitiesOnly yes
  PermitLocalCommand yes
  ServerAliveInterval 60
  ServerAliveCountMax 5
  TCPKeepAlive yes

Host MY_KVM_HOST_1
  HostName MY_KVM_HOST_1
  User root
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  IdentityFile ~/.ssh/id_ansible
  LogLevel ERROR
```
