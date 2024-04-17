# "monitor" will handle qemu guest agent events to force time resync after domain started.
#   Required for prompt guest time correction after resuming from saved state.
#   On host reboot the script cannot run in time to collect events from domains that are
#   started via libvirtd autostart.
#   To effectively handle host reboots the domains should not be configured to autostart,
#   but should be listed in the vmStartupCommands section of config.json file. This file is processed
#   only once when this script starts

# "listener" will listen for https requests on given port to start/stop/save VMs
#   Call like curl "https://yourkvmhost.tld:10000/?key=YOURPSK&cmd=start&target=VMNAME"

# "startup" will start provided list of vms when VMMonitor service is started (e.g.: at host boot)
#   Allows delay statements to space out VM launches

from threading import Thread
import syslog

import libvirt_monitor
import mylog
import confloader
import vmbootprocessor
import serverlistener
import os
import signal

##############################################################
class VMMonitor:
    def __init__(self):
        self.monitor = None
        self.serverListener = None

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self.load_config( "config.json" )
        self.workerThreads = []

    def load_config(self, config_path):
        try:
            loader = confloader.ConfigurationLoader(config_path)
            self.config = loader.load()
        except ValueError as e:
            mylog.log(e)
            exit()

    def exit_gracefully(self, signum, frame):
        if self.monitor is not None:
            self.monitor.shutdown()
        if self.serverListener is not None:
            self.serverListener.shutdown()

    def run(self):
        # monitor running first if enabled so domains launched by startup commands get handled
        if self.config['monitor']['enabled'] == True:
            self.monitor = libvirt_monitor.LibvirtMonitor()
            self.workerThreads.append( self.monitor.thread )

        # one-time startup domains listed in config
        if self.config['startup']['enabled'] == True:
            self.starup = vmbootprocessor.vmBootProcessor(self.config['startup'])

        # listener
        if self.config['listener']['enabled'] == True:
            self.serverListener = serverlistener.ServerListener( self.config['listener'] )
            self.workerThreads.append( self.serverListener.thread )
        

        # wait for threads to exit (foreverish)
        for thread in self.workerThreads:
            if thread.is_alive():
                thread.join()


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

syslog.openlog("vmmonitor")
mylog.log(f"VMMonitor starting.")

monitor = VMMonitor()

monitor.run()