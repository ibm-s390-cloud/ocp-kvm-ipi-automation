# OpenShift on KVM IPI Installation Automation for IBM zSystems / LinuxONE (and IBM Power Systems and Intel / AMD x86_64 and ARM64)

This repository contains Ansible playbooks to install an OpenShift cluster via the OpenShift installer 'IPI' method (installer-provisioned infrastructure) using KVM and libvirt on a dedicated Linux host.
The primary focus of these playbooks is installating and configuring OpenShift on IBM zSystems / LinuxONE hosts (architecture: s390x) but IBM Power System hosts (architecture: ppc64le), Intel-based hosts (architecture: x86_64) and ARM64-based hosts (architecture: aarch64) are also supported.

## Documentation

Please make sure to read the included project [documentation](docs/DOCUMENTATION.md) thoroughly before you get started.

For frequently asked questions please refer to the [FAQ](docs/FAQ.md) document.

If you've encountered an issue while using the playbooks in this repository you might want to take a look at the [troubleshooting](docs/TROUBLESHOOTING.md) document.

## Contributing

Contributions to this project have to be submitted under the Apache License, Version 2.0. See the included [LICENSE](LICENSE) file for more information.

## Developer Certificate of Origin

When making contributions to this project, you certify the [Developer Certificate of Origin](https://developercertificate.org/).

## Submitting Changes

Create GitHub pull requests to contribute changes to this project. Create separate pull requests for each logical enhancement, feature, or problem fix.

You can use GitHub issues to report problems and suggest improvements.

## License

The OpenShift on KVM IPI Installation Automation for IBM zSystems / LinuxONE project and all files included are licensed under the Apache License, Version 2.0. See the included [LICENSE](LICENSE) file for more information.

## Maintainers

- Dirk Haubenreisser (haubenr@de.ibm.com)
