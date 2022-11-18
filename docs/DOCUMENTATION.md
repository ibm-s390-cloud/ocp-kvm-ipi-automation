# Documentation

## Purpose / Target Audience

The playbooks in this repository are intended for setting up OpenShift clusters on Linux hosts that will be used for demonstration, education or proof-of-concept type purposes and thus are short-lived by intent. These playbooks are not meant to set up OpenShift clusters for production purposes or any kind of production-level workloads. Please note that OpenShift clusters set up by these playbooks will neither be supported by Red Hat nor IBM.

## Prerequisites

In order to run the Ansible playbooks in this repository you need:

- an Ansible **compatible** workstation (a dedicated standalone workstation that is physically separate from the target Linux host)
- a working **Ansible 2.10 (or newer)** installation on your workstation
- a suitably powerful Linux host:
  - running one of the following operating systems:
    - RHEL 8.4 (with an **active** Red Hat subscription)
    - RHEL 8.5 (with an **active** Red Hat subscription)
    - RHEL 8.6 (with an **active** Red Hat subscription)
    - RHEL 8.7 (with an **active** Red Hat subscription)
    - RHEL 9.0 (with an **active** Red Hat subscription)
    - RHEL 9.1 (with an **active** Red Hat subscription)
    - Fedora 35
    - Fedora 36
  - using one of the following hardware architectures:
    - s390x (an IBM zSystems / LinuxONE LPAR, supported: z13 / z14 / z15 / z16)
    - ppc64le (an IBM Power Systems bare metal host or LPAR, supported: POWER9)
    - x86_64 (an Intel- or AMD-based bare metal host)
    - aarch64 (an ARM64-based bare metal host)
- a working SSH connection to that Linux host from your workstation user account to the host's *root* acccount (password-less SSH)
- the OpenShift cluster image pull secrets file - see also [here](../ansible/secrets/README.md) for details

Installing Ansible on your workstation should be fairly easy. Please refer to the Ansible installation guide [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for detailed instructions.

### Using Ansible on Microsoft Windows operating systems

Unfortunately as of today Ansible is not fully compatible with Microsoft Windows, meaning a workstation that runs Microsoft Windows is not capable of running Ansible natively. There are however several options for Microsoft Windows users to run Ansible in a Linux-like environment:

- using Windows Subsystem for Linux (WSL)
- using Cygwin

Using WSL in order to run Ansible on a Microsoft Windows workstation is recommended. In order for WSL to work properly you would need to run a recent Microsoft Windows 10 or Windows 11 build and a workstation that supports hardware virtualization features like Intel VT-x or AMD AMD-V. Before you can use WSL on your workstation make sure that the corresponding hardware virtualization features are enabled in your workstation's BIOS. Also make sure that you have the following BIOS features *enabled* on your workstation:

- Execute Disable (XD) or No Execute (NX)

Once you've ensured that the BIOS settings of your workstation have been updated and properly support virtualization make sure to follow these steps to install and configure WSL in Microsoft Windows:

```shell

# open a PowerShell terminal (as administrator) and run the following commands from within that terminal

# enable the WSL capabilities built into Windows
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# reboot your workstation at this point

# download and install the WSL version 2 kernel update
$url = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
$output = "$env:temp\wsl_update_x64.msi"
Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
msiexec.exe /package $output

# use WSL version 2
wsl --set-default-version 2

# reboot your workstation again at this point

# download and install Ubuntu 20.04 for WSL version 2
$url = "https://aka.ms/wsl-ubuntu-2004"
$output = "$env:temp\wsl-ubuntu-2004_x64.appx"
Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
Add-AppxPackage $output

# install and start Ubuntu 20.04
ubuntu2004.exe
```

With Ubuntu 20.04 successfully running in WSL, you can install Ansible and all prerequisite software within that Ubuntu environment like this:

```shell
sudo apt-get update
sudo apt-get install -y ansible
```

## Preparations

### Ansible workstation (your workstation)

Before you can actually run the Ansible playbooks you need to configure your Ansible inventory and your KVM host details. To do so simply follow these steps:

```bash
# clone this repository to your local workstation
cd <somewhere_on_your_local_workstation>
git clone https://github.com/ibm-s390-cloud/ocp-kvm-ipi-automation.git

# chdir into the 'ansible' subdirectory
cd ocp-kvm-ipi-automation/ansible

# create a copy of the 'inventory.template' file
cp inventory.template inventory

# edit your 'inventory' file and replace the placeholder '$$YOUR_KVM_HOST_NAME$$' with the name of your remote Linux host
# make sure to put your Linux host into the correct host group in the 'inventory' file according to the hardware
# architecture of your Linux host
# (make sure you can actually SSH into the host as *root* user, see section Preferences above)
# delete all empty host groups (empty meaning: there are no hosts for that particular hardware architecture) from your inventory file as empty host groups or the presence of any kind of placeholder strings (e.g. '$$YOUR_KVM_HOST_NAME$$') might prevent Ansible from working properly

# put the OpenShift cluster image pull secrets file you've obtained in the subdirectory 'secrets' and name it '.ocp4_pull_secret'
# (don't worry, it won't be persisted in git!)

# chdir into the 'host_vars' subdirectory
cd host_vars

# create a copy of the 'host.yml.template' file and name it '$$YOUR_KVM_HOST_NAME$$.yml' (make sure to replace the placeholder with the name of your remote Linux host - the name of the YAML file must match the host name you've configured in your 'inventory' file in the previous step)
cp host.yml.template $$YOUR_KVM_HOST_NAME$$.yml

# edit your '$$YOUR_KVM_HOST_NAME$$.yml' configuration file and adapt it according to your needs / usage scenario / capabilities of your Linux host
```

Once you've finished with these preparations you can proceed to the actual OpenShift cluster installation.

### Linux host

**You need to start with a vanilla installation of the base operating system! This is very important as any existing KVM-based OpenShift cluster installation or remaining artifacts / configuration snippets thereof are very likely to interfere with the different setup and configuration steps done by these playbooks.**

Once the initial operating system installation is done, simply transfer your public SSH key to the target Linux host's *root* user account:

```bash
ssh-copy-id -i $HOME/.ssh/id_rsa root@$$YOUR_KVM_HOST_NAME$$
```

Make sure that your target Linux host has a working Python3 installation. You can do so by running the following command:

```bash
ssh root@$$YOUR_KVM_HOST_NAME$$ 'yum install -y python3'
```

That is it, everything else (in terms of host configuration / customization) is done by the Ansible playbooks in this repository.

### A note on IBM Power Systems

These playbooks have been successfully tested on an IBM Power System LC922 bare metal server running Red Hat Enterprise Linux 8.5. Tests on older POWER8-based hardware were not successful however as some virtualization features required by RHOCP running on top of KVM and libvirt are not available on that type of hardware.

Please note that Red Hat has issued a deprecation notice for KVM on IBM Power Systems that makes using these playbooks on POWER10 hardware less feasible. For more details please check out this link: <https://access.redhat.com/articles/6005061>.

## The Ansible playbooks

The OpenShift cluster installation on the target Linux host is split into three separate playbooks:

- setup_host.yml
  - prepares the Linux host for running KVM workloads, e.g:
    - installs required software packages
    - configures SELinux
    - configures required networking settings
    - configures required firewall settings
    - configures haproxy for a load-balanced cluster setup
    - configures basic libvirt settings

- prepare_ocp_install.yml
  - prepares the actual OpenShift cluster installation:
    - downloads and builds the chosen 'openshift-install' binary
    - creates directories required by the OpenShift cluster installation process
    - downloads and installs the appropriate 'oc' and 'opm' client tools

- run_ocp_install.yml
  - runs the actual OpenShift cluster installation using 'openshift-install':
    - generates the cluster manifest files
    - adapts the generated manifest files to the user's (your) needs
    - installs OpenShift
    - adds SSH connection profiles for all OpenShift cluster nodes for user 'root'
    - installs and configures vbmc and IPMI (if configured)

All this is done **automatically** - no user interaction or any manual intervention is required whatsoever! On a fairly powerful Linux host the whole OpenShift cluster installation process (including host setup etc.) should not take more than 45 minutes.

To kick off the OpenShift installation process you can either run the Ansible playbooks individually or use the main playbook entrypoint 'site.yml':

```bash
cd ansible

# install / update Ansible prerequites
ansible-galaxy collection install -r requirements.yml --force

# run all playbooks
ansible-playbook -i inventory site.yml

# run playbooks individually
ansible-playbook -i inventory setup_host.yml
ansible-playbook -i inventory prepare_ocp_install.yml
ansible-playbook -i inventory run_ocp_install.yml
```

When the OpenShift cluster installation has finished successfully, you'll get a corresponding Ansible message. At that point the *root* user's account on the target Linux host is properly configured with the OpenShift client tooling and the appropriate `/root/.kube/config` file is present. For more information please refer to the section [State of the KVM host after OpenShift cluster installation has finished successfully](#state-of-the-kvm-host-after-openshift-cluster-installation-has-finished-successfully) in this document.

For OpenShift cluster cleanup purposes there's a dedicated Ansible playbook included in this repository: `cleanup_ocp_install.yml`. This playbook attempts to destroy an existing OpenShift cluster (using 'openshift-install') and delete all stale resources that were used by the previously existing cluster / cluster installation attempt. Run the cleanup playbook like this:

```bash
cd ansible

# note the optional parameter 'cleanup_ignore_errors' which ensures that the cleanup playbook
# will finish successfully regardless of any errors encountered while running the individual cleanup tasks
ansible-playbook -i inventory cleanup_ocp_install.yml [-e cleanup_ignore_errors=true]
```

The cleanup playbook can also take care of de-registering the OpenShift cluster that is being destroyed from OpenShift Cluster Manager (OCM). For details on how to enable this OCM integration please refer to [here](../ansible/secrets/README.md).

## State of the KVM host after OpenShift cluster installation has finished successfully

When the OpenShift cluster installation was successful you can interact with it in the usual ways. If you want to use the OpenShift client tooling from the command line (using `oc` or `kubectl`) you can do so by logging into the *root* user's account via SSH and just type away - the tools have been installed as part of the automated cluster installation via the Ansible playbooks. The 'kubeconfig' file is present in `/root/.kube/config` should you be looking for it.
All other files that have been generated by the OpenShift cluster installation (by running the OpenShift installer binary 'openshift-install') can be found in the directory `/root/ocp4-workdir`, including the login password for the 'kubeadmin' user: `/root/ocp4-workdir/auth/kubeadmin-password`.

For ease-of-use the *root* user's SSH configuration contains entries for all OpenShift cluster nodes (except the ephemeral bootstrap node). You can look up the available SSH connection profiles via `cat /root/.ssh/config`.

If you've set the host variable `setup_vbmc_ipmi` to `true` in your '$$YOUR_KVM_HOST_NAME$$.yml' configuration file, `vbmc` and IPMI will be setup and configured automatically for all OpenShift cluster nodes (except the ephemeral bootstrap node). You'll find the corresponding IPMI connection information in the file `/root/ocp4-workdir/ipmi_config.yaml`. Please note that this file is generated automatically with each new OpenShift cluster installation, meaning the login information stored in this file is only valid for the *current* OpenShift cluster instance.

## Auxiliary playbooks

In addition to the main Ansible playbooks mentioned above this repository contains the following auxiliary playbooks:

- tune_ocp_install.yml
  - see [here](../ansible/roles/tuning/README.md) for detailed information

- enable_crypto_resources.yml
  - see [here](../ansible/roles/crypto/README.md) for detailed.information

- reboot_host.yml
  - reboots the targeted KVM host and waits until the host has finished rebooting

- start_ocp_cluster_nodes.yml
  - starts the OpenShift cluster nodes using libvirt

- check_ocp_cluster_state.yml
  - runs a basic health check for the OpenShift cluster on the KVM host:
    - checks the status of all cluster nodes and reports all non-ready nodes (if any)
    - checks the status of all ClusterOperator resources and reports all unavailable ClusterOperators (if any)
    - queries the cluster's Prometheus instance for any active alerts and reports them (if any)

Please note that these auxiliary playbooks are not required to setup/install a fully functional OpenShift cluster. This can be achieved solely by using the main playbooks mentioned above.

You can run the auxiliary playbooks like this:

```bash
cd ansible

# reboot the KVM host
ansible-playbook -i inventory reboot_host.yml

# start the OpenShift cluster nodes (e.g. after a KVM host reboot was performed)
ansible-playbook -i inventory start_ocp_cluster_nodes.yml

# tune the installed OpenShift cluster on the targeted KVM host
# (this will mainly reconfigure the KVM guests and KVM network settings)
ansible-playbook -i inventory tune_ocp_install.yml

# attach existing crypto resources to the cluster worker nodes and install / configure the Kubernetes CEX device plugin
ansible-playbook -i inventory enable_crypto_resources.yml

# check the basic OpenShift cluster health
ansible-playbook -i inventory check_ocp_cluster_state.yml
```

## Caveats

While it is theoretically possible to install multiple OpenShift clusters on the same Linux KVM host, the Ansible playbooks in this repository have been designed and implemented with a *single* OpenShift cluster in mind. That means that in case there is an existing OpenShift cluster already running on your target Linux host (likely installed manually via UPI) these playbooks should not be used to establish *yet another* OpenShift cluster. It is recommended to destroy the existing cluster first (e.g. by utilizing the 'cleanup_ocp_install.yml' playbook) before attempting another installation.

While the OpenShift cluster installation on a reasonably powerful Linux host is quite fast, there might be occasions where the installation runs into some sort of timeout that is imposed by these Ansible playbooks. For the cluster installation itself, this timeout is set to 3600 seconds (one hour).

For more information please see also the included [troubleshooting](TROUBLESHOOTING.md) document.

## Running the playbooks from within a Docker container

This repository includes a Dockerfile that can be used to build a Docker image containing Ansible (and all packages required by Ansible) and the KVM IPI automation playbooks. This Docker image can then either be used as the base image for further customizations (e.g. adding your own playbooks or roles on top of the existing ones) or as-is in order to run the playbooks against any appropriate Linux KVM host directly.

### Building the Docker image yourself

In order to build the Docker image you need either a working Docker or podman instance installed on your local workstation. Building the Docker image is fairly simple and can be done by running the following commands:

```bash
# if you're using Docker
docker build . -t kvm-ipi-automation:base-latest

# if you're using podman
podman build . -t kvm-ipi-automation:base-latest --format docker
```

### Using the Docker image as the base image for further customization

Due to the way the The KVM IPI automation Docker image content has been structured, it's fairly easy to extend the image by adding additional Ansible roles or playbooks. The content of the Docker image is as follows (only the Ansible-related parts of the image are shown here):

```bash
ansible
├── ansible.cfg
├── check_ocp_cluster_state.yml
├── cleanup_ocp_install.yml
├── enable_crypto_resources.yml
├── filter_plugins
│   └── FilterUtils.py
├── group_vars
│   ├── aarch64_kvm_host.yml
│   ├── all.yml
│   ├── ppc64le_kvm_host.yml
│   ├── s390x_kvm_host.yml
│   └── x86_64_kvm_host.yml
├── inventory.template
├── prepare_ocp_install.yml
├── reboot_host.yml
├── requirements.yml
├── roles
│   ├── basics
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   └── golang.profile.sh
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       ├── install_python_packages.yml
│   │       └── main.yml
│   ├── common
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── vars
│   │       └── main.yml
│   ├── crypto
│   │   ├── README.md
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   ├── cex-plugin-daemonset.yaml
│   │   │   ├── ep11
│   │   │   │   └── README.md
│   │   │   └── vfio_ap.conf
│   │   ├── library
│   │   │   ├── crypto_adapter.py
│   │   │   ├── crypto_adapter_info.py
│   │   │   ├── mdev_libvirt_attach.py
│   │   │   └── mdev_uuid_gen.py
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── tasks
│   │   │   ├── attach_mediated_device_to_domain.yml
│   │   │   ├── main.yml
│   │   │   └── soundness_checks.yml
│   │   └── templates
│   │       ├── cex-resources-config.yaml.j2
│   │       ├── crypto-test-load.yaml.j2
│   │       └── libvirt_hook_qemu.py.j2
│   ├── firewall
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       └── main.yml
│   ├── libvirt
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   └── libvirt.profile.sh
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       ├── enable_monolithic_libvirt.yml
│   │       └── main.yml
│   ├── networking
│   │   ├── files
│   │   │   ├── dnsmasq.add-hosts.conf
│   │   │   ├── dnsmasq.cache.conf
│   │   │   └── networkmanager.dns.conf
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── tasks
│   │   │   └── main.yml
│   │   └── templates
│   │       ├── dnsmasq.openshift.conf.j2
│   │       └── haproxy.cfg.j2
│   ├── ocp_build_installer
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       ├── main.yml
│   │       └── patch_installer.yml
│   ├── ocp_cleanup
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       ├── archive_cluster_ocm.yml
│   │       └── main.yml
│   ├── ocp_install_clients
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       ├── download_client_tarballs.yml
│   │       └── main.yml
│   ├── ocp_install_cluster
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   └── 03_openshift-machineconfigpool_infra-0.yaml
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── tasks
│   │   │   ├── copy_advanced_configuration_files.yml
│   │   │   ├── main.yml
│   │   │   ├── setup_infra_cluster_nodes.yml
│   │   │   └── update_master_configuration.yml
│   │   └── templates
│   │       ├── 01_openshift-cluster-api_infra-machineset-0.yaml.j2
│   │       ├── 02_openshift-machineconfig_99-infra-ssh.yaml.j2
│   │       ├── install-config.yaml.j2
│   │       └── libvirt_network_dns_xml.j2
│   ├── ocp_install_cluster_wrapup
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── tasks
│   │   │   ├── main.yml
│   │   │   ├── persist_libvirt_cluster_network.yml
│   │   │   └── persist_ssh_config.yml
│   │   └── templates
│   │       └── ssh-config.j2
│   ├── ocp_prepare_install
│   │   ├── files
│   │   │   └── njmon_linux_v80.patch
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       └── main.yml
│   ├── selinux
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       └── main.yml
│   ├── soundness_check
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       └── main.yml
│   ├── tuning
│   │   ├── README.md
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   ├── 50-enable-rfs.yaml
│   │   │   └── thp-workers-profile.yaml
│   │   ├── meta
│   │   │   └── main.yml
│   │   └── tasks
│   │       ├── k8s_disable_thps.yml
│   │       ├── k8s_enable_rfs.yml
│   │       ├── libvirt_add_iothreads.yml
│   │       ├── libvirt_disable_memballoon.yml
│   │       ├── libvirt_optimize_disks.yml
│   │       ├── libvirt_optimize_network.yml
│   │       ├── libvirt_set_cpu_shares.yml
│   │       └── main.yml
│   └── vbmc
│       ├── defaults
│       │   └── main.yml
│       ├── files
│       │   └── dummy.conf
│       ├── meta
│       │   └── main.yml
│       ├── tasks
│       │   └── main.yml
│       └── templates
│           └── ipmi_config.yaml.j2
├── run_ocp_install.yml
├── run_soundness_checks.yml
├── setup_host.yml
├── site.yml
├── start_ocp_cluster_nodes.yml
├── tasks
│   ├── check_cluster_state.yml
│   ├── get_cluster_name.yml
│   ├── get_cluster_uid.yml
│   ├── get_resolv_conf_location.yml
│   ├── reboot_host.yml
│   ├── start_cluster_nodes.yml
│   └── wait_for_cluster.yml
├── test_plugins
│   └── TestUtils.py
└── tune_ocp_install.yml
```

As you can see the user-specific files required by Ansible to actually run the playbooks are missing from the Docker image - notably the main 'inventory' file, the 'host_vars' and 'host_files' directories containing host-specific variables as well as the 'secrets' directory. Without these files the Docker image is not fully functional per se, the user has to provide these files before the Ansible playbooks within the image can be used.

This is where the Docker image customization aspect comes in.

To use the Docker image as the base image for further customization, simply build or download the image following the instructions given above. Afterwards create your own Dockerfile and add whatever you like to the base image, e.g.:

```yaml
FROM kvm-ipi-automation:base-latest

# make sure everything is done as 'root' user
USER root

# set the working directory of the image to '/ansible'
WORKDIR /ansible

# e.g. add a new role 'myrole' to the existing set of roles
ADD myrole roles/myrole

# e.g. add a new playbook 'myplaybook.yml' to the existing playbooks
ADD myplaybook.yml myplaybook.yml

# e.g. install a required Ansible collection
RUN ansible-galaxy collection install containers.podman

# add a fixed 'inventory' file (which is deliberately omitted from the base image)
ADD inventory inventory

# add a fixed 'host_vars' directory (which is deliberately omitted from the base image)
ADD host_vars host_vars

# add a fixed 'host_files' directory (which is deliberately omitted from the base image)
ADD host_files host_files

# add EP11 binary packages to be installed on the host (optional, s390x only)
COPY ep11-host-*s390x.rpm roles/crypto/files/ep11/

# add some more stuff...
# ATTENTION: Be careful to not overwrite any existing roles and playbooks
# from the base image (unless you're exactly knowing what you're doing)!
```

### Running the Docker image as-is

If you do not want to customize the KVM IPI automation Docker image but rather use it as-is you need to make sure to mount all files and directories required by Ansible into the Docker container at runtime. For this you'll have to use volume mounts for the following assets:

- /ansible/inventory
- /ansible/host_vars
- /ansible/host_files
- /ansible/secrets
- /ansible/roles/crypto/files/ep11
- /root/.ssh

You can use the following commands as an example on how to run the main Ansible playbook 'site.yml' from within a Docker container using volume mounts to mount the required files and directories into the container:

```bash
# if using Docker
docker run --rm -ti -v $HOME/.ssh:/root/.ssh:rw -v $PWD/ansible/inventory:/ansible/inventory:ro -v $PWD/ansible/host_vars:/ansible/host_vars:ro -v $PWD/ansible/host_files:/ansible/host_filess:ro -v $PWD/ansible/secrets:/ansible/secrets:ro -v $PWD/ansible/roles/crypto/files/ep11:/ansible/roles/crypto/files/ep11:ro --rm kvm-ipi-automation:base-latest ansible-playbook -i inventory site.yml

# if using podman
podman run --rm -ti -v $HOME/.ssh:/root/.ssh:rw -v $PWD/ansible/inventory:/ansible/inventory:ro -v $PWD/ansible/host_vars:/ansible/host_vars:ro -v $PWD/ansible/host_files:/ansible/host_filess:ro -v $PWD/ansible/secrets:/ansible/secrets:ro -v $PWD/ansible/roles/crypto/files/ep11:/ansible/roles/crypto/files/ep11:ro --rm kvm-ipi-automation:base-latest ansible-playbook -i inventory site.yml
```
