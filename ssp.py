#!/usr/bin/python
import SimpleHTTPServer
import SocketServer
import sys

PORT = 8888

# http://stackoverflow.com/a/25375077
class SSPHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        print("[%s]: %s ==> %s" % (self.log_date_time_string(), self.client_address[0], format%args))


class sspserver():
	
	def __init__(self):
		Handler = VanHTTPHandler
		httpd = SocketServer.TCPServer(("", PORT), Handler)
		print "Serving on port", PORT
		httpd.serve_forever()
		
if __name__ == "__main__":
	s = sspserver()