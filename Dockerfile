FROM registry.access.redhat.com/ubi8/python-38

# use 'root' user throughout the whole image
USER root

# set the correct language settings
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# install required OS-level packages
RUN dnf upgrade -y && \
    dnf module install -y rust-toolset:rhel8/common && \
    dnf install -y gcc-gfortran jq wget curl && \
    dnf clean all

# install Ansible and prerequisite tooling
RUN pip install --upgrade pip setuptools wheel && \
    pip install ansible jmespath

# copy 'ansible' subdirectory into image
ADD ansible /ansible

# set the global working directory
WORKDIR /ansible

# install required Ansible collections
RUN ansible-galaxy install -r requirements.yml

# deliberately do not set an entrypoint or command
# this will use the Docker default which is set to '/bin/sh -c'
