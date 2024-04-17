import libvirt
from threading import Thread
import time
from typing import List
import mylog
import syslog
import os

class vmBootProcessor:
    def __init__(self, startupConfig):

        if 'vmStartupCommands' in startupConfig:
            self.conn = libvirt.open("qemu:///system")
            self.start_domains( startupConfig['vmStartupCommands'] )
            mylog.log( f"Processed VM startup commands")
            self.conn.close()
        else:
            mylog.log( f"No startup commands found" )

    def start_domains(self, lines: List[str]) -> None:
            # array to hold threads used to launch VMs
            domainThreads = []

            # process config lines
            for line in lines:
                try:
                    self.handle_config_line( line, domainThreads )
                except Exception as e:
                    mylog.log( f"Error in config handling: {line} - {str(e)}", syslog.LOG_ERR )

            for thread in domainThreads:
                if thread.is_alive():
                    thread.join()

    def handle_config_line(self, input_string, domainThreads):
            # interpret config line

            # strip whitespaces and check if input is valid
            input_string = input_string.strip()
            if len(input_string) > 0 and not input_string.startswith("#"):
                # split the input into command and value
                command, *value = input_string.split()

                if command == 'delay':
                    # sleep for n seconds
                    print(f"Sleeping {int(value[0].strip())}")
                    time.sleep(int(value[0].strip()))
                elif command == 'start':
                    # start domain if not already running
                    domainName = value[0].strip()
                    domain = self.conn.lookupByName( domainName)
                    state,reason = domain.state()
                    if state == libvirt.VIR_DOMAIN_RUNNING:
                        msg = f"Domain {domain.name()} already running."
                        mylog.log( msg )
                    else:
                        # create a thread to create the domain
                        thread = Thread( target=self.create_domain, args=( domain, ))
                        thread.daemon = True
                        domainThreads.append( thread )
                        thread.start()
                elif command == 'suspend':
                    # do another day
                    pass
                else:
                    print("Invalid command")
                    return
                
    def create_domain( self, domain ):
        mylog.log( f"Starting {domain.name()}" )
        domain.create()

#######################################################