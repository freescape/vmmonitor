import libvirt
import libvirt_qemu
from threading import Thread
import time
from typing import List
import mylog
import syslog

class LibvirtMonitor:
    exit_now = False
    def __init__(self):
       
        try:
            libvirt.virEventRegisterDefaultImpl()
            self.conn = libvirt.open("qemu:///system")
            self.callback_id = self.conn.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_AGENT_LIFECYCLE, self._callback, None)
        except Exception as e:
            mylog.log(f"Error initializing LibvirtMonitor: {str(e)}", syslog.LOG_ERR )
            raise

        self.thread = Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()        

    def shutdown(self):
        self.conn.domainEventDeregisterAny(self.callback_id)
        self.conn.close()
        mylog.log("Shutting down monitor thread")
        self.exit_now = True

    def run(self):
        while self.exit_now == False:
            try:
                libvirt.virEventRunDefaultImpl()
            except Exception as e:
                mylog.log( f"Error in event loop:{str(e)}", syslog.LOG_ERR)
            finally:
                time.sleep(1)

    def _callback(self, conn, dom, event, detail, opaque):
        # mylog.log("event callback")
        # callback for libvirt guest agent lifecycle event
        if event == libvirt.VIR_CONNECT_DOMAIN_EVENT_AGENT_LIFECYCLE_STATE_CONNECTED and detail == libvirt.VIR_DOMAIN_EVENT_STARTED_RESTORED:
            # this also gets called when starting from non-saved state, but calling update time when not needed seems harmless
            domain_name = dom.name()
            mylog.log(f"VM {domain_name} agent reconnected. Running restore actions." )
            self.update_time( dom )

    def update_time(self, domain):
        ret = libvirt_qemu.qemuAgentCommand(domain, '{"execute": "guest-set-time"}', timeout=10, flags=0)
        mylog.log( f"{domain.name()} qemu time cmd return:{ret}" )


