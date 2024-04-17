import ssl
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import urllib.parse as urlparser
import domain_actions
import mylog
import syslog

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparser.urlparse(self.path)
        query_params = dict(qc.split("=") for qc in parsed_path[4].split("&"))
        self.server_version = "BHTTP1.1"
        self.disable_nagle_algorithm = True
        self.protocol_version = "HTTP/1.1"

        if 'key' not in query_params or 'cmd' not in query_params or query_params["key"] != config["key"] :
            responseCode = 400
            responseData = 'bad request kc'
            time.sleep(5.0)
        elif 'target' not in query_params :
            responseCode = 400
            responseData = 'bad request t'
        else :
            responseCode = 200
            target = query_params["target"]
            cmd = query_params["cmd"]
            responseData = 'OK'

            if cmd == "wake" or cmd == "start":
                responseData = f"starting {target}"
                dom = domain_actions.domainAction()
                responseData = responseData + "\r\n" + dom.createAndWait( domainName=target )
            elif cmd == "stop" and 'stop' in config['commandsEnabled'] and config['commandsEnabled']['stop'] == True:
                responseData = f"stopping {target}"
                dom = domain_actions.domainAction()
                responseData = responseData + "\r\n" + dom.stop( domainName=target )
            elif cmd == "save" and 'save' in config['commandsEnabled'] and config['commandsEnabled']['save'] == True:
                responseData = f"saving {target}"
                dom = domain_actions.domainAction()
                responseData = responseData + "\r\n" + dom.save( domainName=target )                
            else :
                responseData = "unsupported cmd"

        responseData = responseData + "\r\n"

        self.send_response( responseCode )
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len( responseData ) )
        self.end_headers()
        self.wfile.write( responseData.encode("utf-8") )
        self.wfile.flush()

class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6


class ServerListener:

    def __init__(self, config):
        self.httpd = None
        self.config = config
        self.thread = Thread( target=self.start_listening )
        self.thread.daemon = True
        self.thread.start()

    def start_listening(self):
        if self.config:
            global config
            global vm
            config = self.config

            try:
                httpd = HTTPServerV6(('::', self.config["port"]), Handler)
                sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                sslcontext.load_cert_chain(self.config["certificate"]["path"], self.config["certificate"]["keyPath"], password=self.config["certificate"]["password"])
                httpd.socket = sslcontext.wrap_socket(httpd.socket, server_side=True)
                httpd.allow_reuse_address = True
            except Exception as e:
                mylog.log(f"Error launching server: {str(e)}", syslog.LOG_ERR )
                return
            
            self.httpd = httpd
            httpd.serve_forever()
        else:
            print("Couldn't load configuration. Exiting.")
    
    def shutdown( self ):
        if self.httpd is not None:
            mylog.log("Shutting down listener")
            self.httpd.shutdown()
