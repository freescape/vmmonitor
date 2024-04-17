import libvirt
from threading import Thread
from typing import List
import mylog
import syslog

class domainAction :

    def createAndWait( self, domainName ) :
        try:
            self.conn = libvirt.open("qemu:///system")
            domain = self.conn.lookupByName( domainName )
            state,reason = domain.state()
            if state == libvirt.VIR_DOMAIN_RUNNING:
                msg = f"Domain {domain.name()} already running."
            else:
                msg =  f"Starting {domain.name()}" 
                domain.create()
        except Exception as e:
           mylog.log(f"Error in domainAction: {str(e)}", syslog.LOG_ERR )
           msg = str(e)

        if isinstance( self.conn, libvirt.virConnect ) :
            self.conn.close()

        mylog.log( msg )
        return msg

    def stop( self, domainName ) :
        try:
            self.conn = libvirt.open("qemu:///system")
            domain = self.conn.lookupByName( domainName )
            state,reason = domain.state()
            if state != libvirt.VIR_DOMAIN_RUNNING:
                msg = f"Domain {domain.name()} not running."
            else:
                msg =  f"Stopping {domain.name()}" 
                domain.shutdown()
        except Exception as e:
           mylog.log(f"Error in domainAction: {str(e)}", syslog.LOG_ERR )
           msg = str(e)

        if isinstance( self.conn, libvirt.virConnect ) :
            self.conn.close()

        mylog.log( msg )
        return msg

    def save( self, domainName ) :
        try:
            self.conn = libvirt.open("qemu:///system")
            domain = self.conn.lookupByName( domainName )
            state,reason = domain.state()
            if state != libvirt.VIR_DOMAIN_RUNNING:
                msg = f"Domain {domain.name()} not running."
            else:
                msg =  f"Saving {domain.name()}" 
                domain.managedSave()
        except Exception as e:
           mylog.log(f"Error in domainAction: {str(e)}", syslog.LOG_ERR )
           msg = str(e)

        if isinstance( self.conn, libvirt.virConnect ) :
            self.conn.close()

        mylog.log( msg )
        return msg
