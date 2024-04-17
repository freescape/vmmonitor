
# VMMonitor
**A simple KVM/QEMU tool**
- Monitor for libvirt domain state changes to execute time sync immediately after domain is started or resumed
- Automate domain starting to enable staggering VM launches with delays
- Provide a simple https interface for starting/stopping/saving VMs


## monitor

If enabled, "monitor" will handle qemu guest agent events to force time resync after domain started.
 
This is needed for prompt guest time correction after resuming from saved state, and requires the qemu-guest-agent to be installed on the guest VM.

On host reboot the script cannot run in time to collect events from domains that are started via libvirtd autostart. To effectively handle host reboots the domains should not be configured to autostart, but should be listed in the vmStartupCommands section of config.json file. This file is processed only once when this script starts

## listener

If enabled, "listener" will listen for https requests on given port to start/stop/save VMs
Pass via querystring three parameters:
- key
- cmd
- target

E.g.
> curl "https://yourkvmhost.tld:10000/?key=YOURPSK&cmd=start&target=VMNAME"

## startup 

If enabled, "startup" will start the defined list of VMs when the VMMonitor service is started (e.g.: at host boot)

The use of "delay N" statements allows staggering the launching of VMs. Refer to the config sample for example.

# Install

- Copy the files to a suitable destination (e.g. /opt/vmmonitor)
- Run the **install.sh** file in there
- Will install the python script as a service and create a user to run as
- Requires Python 3
