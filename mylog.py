import syslog

def log( msg , level = syslog.LOG_INFO ):
    print( msg )
    syslog.syslog( level, msg )   