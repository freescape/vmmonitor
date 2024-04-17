
# VMMonitor
**A simple KVM/QEMU tool**
- Monitor for libvirt domain state changes to execute time sync immediately after domain is resumed
- Automate domain starting to enable staggering VM launches with delays
- Provide a simple https interface for starting/stopping/saving VMs


## monitor

If enabled, "monitor" will handle qemu guest agent events to force time resync after domain started.
 
This is needed for prompt guest time correction after resuming from saved state.

Requires the qemu-guest-agent to be installed on the guest VM.

Upon host reboot the script cannot run in time to collect events from domains that are started by libvirtd autostart. To effectively handle host reboots the domains should not be configured to autostart, but should be listed in the vmStartupCommands section of config.json file. This file is processed only once when this service starts.

## listener

If enabled, "listener" will listen for https requests on given port to start/stop/save VMs.

Accessed by a GET request passing via querystring three parameters:

- key ( a pre-shared string key )
- cmd ( [start|stop|save|wake] )
- target ( target domain name )

E.g.
> curl "https://yourkvmhost.tld:10000/?key=YOURPSK&cmd=start&target=VMNAME"

## startup 

If enabled, "startup" will start the defined list of VMs when the VMMonitor service is started (e.g.: at host boot)

The use of "delay N" statements allows staggering the launching of VMs. 

E.g.:
>        "vmStartupCommands": [
>            "start vm1",
>            "start vm2",
>            "delay 5",
>            "start vm3",

In this case vm1 and vm2 will be launched simultaneously without waiting for them to complete, followed by a 5 second delay, followed by vm3 being launched.

Refer to the config sample for example.

# Install

- Copy the files to a suitable destination (e.g. /opt/vmmonitor)
- Use config.json.sample to create config.json and edit appropriately
- Run the **install.sh** file in target directory
- This will install the python script as a service and create a user to run as
- Requires Python 3

# Why

I wrote this because I needed guest time to be synchronized quickly after VM restore from saved state. This can otherwise take minutes! This then required the addition of the startup functionality to allow handling of the host reboot case, which then enabled easy staggering of guest VM launching - a nice-to-have.

I separately wanted scripts on some guests to be able to launch other VMs without having any particular permissions on the hypervisor that hosted them, leading to the addition of the https listener.
