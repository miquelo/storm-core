#!/bin/bash

apt-get -y install sudo

# Set up password-less sudo for admin user
echo "${ADMIN_NAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${ADMIN_NAME}
chmod 440 /etc/sudoers.d/${ADMIN_NAME}

# no tty
echo "Defaults !requiretty" >> /etc/sudoers

