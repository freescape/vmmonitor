#!/usr/bin/env bash

if [ "$(id -u)" -ne 0 ]; then
        echo 'This script must be run by root' >&2
        exit 1
fi


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
file="$DIR/vmmonitor.service"

if id vmmonitor >/dev/null 2>&1; then
    echo 'user exists'
else
    echo 'adding user vmmonitor'
    useradd -m vmmonitor
fi

usermod -a -G kvm vmmonitor
usermod -a -G libvirt vmmonitor

chown -R vmmonitor:vmmonitor $DIR
ln -s "$file" "/etc/systemd/system/vmmonitor.service"
systemctl daemon-reload
systemctl enable vmmonitor
systemctl restart vmmonitor
systemctl status vmmonitor
