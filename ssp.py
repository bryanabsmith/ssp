#!/usr/bin/python

# When testing, "sudo lsof -i :<port> and sudo kill -9 <PID>" will close the port if you find Python complaining that a port is in use. Courtesy of http://stackoverflow.com/questions/12397175/how-do-i-close-an-open-port-from-the-terminal-on-the-mac
# If you're testing with the default port of 8888, execute the following to address ""[Errno 48] Address already in use" issues:
#	sudo lsof -i :8888 and sudo kill -9 <PID>

import anydbm
import BaseHTTPServer
import ConfigParser
import datetime
import httpagentparser
import logging
import os
import platform
import SimpleHTTPServer
import SocketServer
import socket
import sys

PORT = 8888
SSP_VERSION = "0.1"
DOCROOT = "."
ITWORKS = "html/index.html"
LOGFILE = "ssp.log"
IP = "0.0.0.0"
PLAT = sys.platform

# This is the default page for "it works!" (ie. the server is successfully loading content). &version& is replaced with the current version of ssp running.
WORKSPAGE = """<!DOCTYPE html5>
<html>
	<head>
		<style>
			body {
				background-color: #eee;
				font-family: 'Verdana', Geneva, sans-serif;
				margin: 10%;
			}

			table {
				border-spacing: 0px;
				border-style: solid;
				border-width: 1px;
			}

			th {
				background-color: #606060;
				color: white;
			}

			th, td {
				padding: 5px;
			}

			.evenRow {
				background-color: #C0C0C0;
			}
		</style>
	</head>
	<body>
		<h3>It works!</h3>

		<table>
			<tr>
				<th>Property</th>
				<th>Value</th>
			</tr>
			<tr>
				<td>Version</td>
				<td>&version&</td>
			</tr>
			<tr class="evenRow">
				<td>Docroot</td>
				<td>&docroot&</td>
			</tr>
			<tr>
				<td>Platform</td>
				<td>&platform&</td>
			</tr>
		</table>
	</body>
</html>

"""

# http://stackoverflow.com/a/25375077
class SSPHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

	# Set the server version
	SimpleHTTPServer.SimpleHTTPRequestHandler.server_version = SSP_VERSION

	# ConfigParser for the Handler class
	config = ConfigParser.RawConfigParser(allow_no_value=True)

	def log_message(self, format, *args):
		"""
			Format the log messages generated by requests to the server.
		"""
		DETAILED = self.config.get("setup", "detailed")
		# Check to see if the user wants detailed logging.
		if DETAILED == "True":
			# Print log messages based on the response code. Each time a request is sent to the server, it responds with a three digit code.
			print("[%s]: %s ==> %s" % (self.log_date_time_string(), self.client_address[0], format%args))
		else:
			# The codes are stored in the second argument of the args array that includes response log messages.
			code = args[1]
			# 200 is OK - this is what we're looking for.

			httpCodes = {"100": "Continue", "101": "Switching Protocols",
						 "200": "OK", "201": "Created", "202": "Accepted", "203": "Non-Authoritative Information", "204": "No Content", "205": "Reset Content", "206": "Partial Content",
						 "300": "Multiple Choices", "301": "Moved Permanently", "302": "Found", "303": "See Other", "304": "Not Modified", "305": "Use Proxy", "307": "Temporary Redirect",
						 "400": "Bad Request", "401": "Unauthorized", "402": "Payment Required", "403": "Forbidden", "404": "Not Found", "405": "Method Not Allowed", "406": "Not Acceptable", "407": "Proxy Authentication Required", "408": "Request Timeout", "409": "Conflict", "410": "Gone", "411": "Length Required", "412": "Precondition Failed", "413": "Request Entity Too Large", "414": "Request-URI Too Long", "415": "Unsupported Media Type", "416": "Requested Range Not Satisfiable", "417": "Expectation Failed",
						 "500": "Internal Server Error", "501": "Not Implemented", "502": "Bad Gateway", "503": "Service Unavailable", "504": "Gateway Timeout", "505": "HTTP Version Not Supported"}

			#if code == "200":
				#code = "OK (200)"
			print("[%s]: %s" % (self.log_date_time_string(), httpCodes[code]))

	# https://wiki.python.org/moin/BaseHttpServer
	def do_HEAD(self):
		# Load the configuration file.
		self.config.read("ssp.config")

		statsDBLocation = self.config.get("stats", "location")
		statsDB = anydbm.open(statsDBLocation, "c")

		# Send a 200 (OK) - request succeeded.
		self.send_response(200)

		# Set the content to html.
		self.send_header("Content-type", "text/html")

		# http://b.leppoc.net/2010/02/12/simple-webserver-in-python/
		headers = self.headers.getheader("User-Agent")
		print(headers)
		# http://shon.github.io/httpagentparser/
		simpleheaders = httpagentparser.simple_detect(headers)
		print(simpleheaders)

		osHeader = str(simpleheaders[0].replace(" ", "_"))
		browserHeader = str(simpleheaders[1].replace(" ", "_"))

		try:
			statsDB["os_%s" % osHeader] = str(int(statsDB["os_%s" % osHeader]) + 1)
		except KeyError:
			statsDB["os_%s" % osHeader] = "1"

		try:
			statsDB["browser_%s" % browserHeader] = str(int(statsDB["browser_%s" % browserHeader]) + 1)
		except KeyError:
			statsDB["browser_%s" % browserHeader] = "1"

		# End the headers.
		self.end_headers()

	# https://wiki.python.org/moin/BaseHttpServer
	def do_GET(self):
		# self.send_response(200)
		# self.send_header("Content-type", "text/html")
		# self.end_headers()

		# Load the configuration file.
		self.config.read("ssp.config")

		password = self.config.get("password", "enabled")
		if password == "yes":
			# http://effbot.org/librarybook/simplehttpserver.htm
			print(self.path)
		# print(self.address_string())

		# "It Works" page.
		itworks = self.config.get("content", "itworks")

		docroot_dir = self.config.get("content", "docroot")

		platformName = platform.system()
		if platformName == "Darwin":
			platformName = "OS X %s" % platform.mac_ver()[0]
		elif platformName == "Windows":
			platformName = "Windows %s" % platform.win32_ver()[0]
		elif platformName == "Linux":
			platformName = "%s Linux (%s)" % (platform.linux_distribution()[0].capitalize(), platform.release())

		# Create the headers.
		self.do_HEAD()

		# Log that headers were sent
		logging.info("headers")

		# Check to see if an index.html or index.htm already exists. If it doesn't, use one set by the user in the config file.
		if os.path.isfile("index.html") == False:
			# This loads the default index file that the user configures.
			#f = open(itworks, "r")
			#self.wfile.write(f.read())
			#f.close()
			default_page = WORKSPAGE.replace("&version&", SSP_VERSION)
			default_page = default_page.replace("&docroot&", docroot_dir)
			default_page = default_page.replace("&platform&", platformName)
			self.wfile.write(default_page)
		# If there is an index.html available, use that.
		elif os.path.isfile("index.html") == True:
			f = open("index.html", "r")
			poweredby = self.config.get("content", "poweredby")
			if poweredby == "true":
				self.wfile.write(f.read() + "<p style='font-family: \"Arial\"; font-size: 10pt; text-align: center;'><span>Powered by ssp/%s.</span></p>" % SSP_VERSION)
			else:
				self.wfile.write(f.read())
			f.close()

		# Open up the stats database.
		statsDBLocation = self.config.get("stats", "location")
		statsDB = anydbm.open(statsDBLocation, "c")

		# Add a value to the total requests
		try:
			statsDB["requests"] = str(int(statsDB["requests"]) + 1)
		except KeyError:
			statsDB["requests"] = "1"

		try:
			year = datetime.datetime.now().year
			month = datetime.datetime.now().month
			day = datetime.datetime.now().day
			statsDB["requests_%s_%s_%s" % (year, month, day)] = str(int(statsDB["requests_%s_%s_%s" % (year, month, day)]) + 1)
		except KeyError:
			statsDB["requests_%s_%s_%s" % (year, month, day)] = "1"

class sspserver():

	def __init__(self):
		"""
			Constructor for main server class.
		"""

		# Setup the configuration parser.
		self.config = ConfigParser.RawConfigParser(allow_no_value=True)

        # OS X config location
		if (PLAT == "darwin"):
			self.config.read("ssp.config")
        # Windows config location
		elif (PLAT == "win32"):
			self.config.read("ssp.config")
        # Linux config location
		elif (PLAT.find("linux") > -1):
			self.config.read("ssp.config")
        # Everything else config location
		else:
			self.config.read("ssp.config")

		# Set the log file.
		LOGFILE = self.config.get("setup", "logfile")

		# Setup the logger.
		# http://stackoverflow.com/q/11581794 - formatting help
		self.logger = logging.basicConfig(filename=LOGFILE, level=logging.DEBUG, format="[%(asctime)s]: %(levelname)s: %(message)s")

		# Log that things got started
		logging.info("ssp started.")

		# Set the port based on the config file.
		PORT = int(self.config.get("setup", "port"))

		# Set the version based on the config file.
		# SSP_VERSION = "ssp/" + self.config.get("setup", "ssp_version")

		# Set the docroot based on the config file.
		DOCROOT = self.config.get("content", "docroot")

		# Set the location of the "It Works" page (the default index.html page).
		# This is now written into the server itself for the purposes of simplifying things.
		# ITWORKS = self.config.get("content", "itworks")

		# Change the working directory to the one specified for the docroot. This ensures that we are serving content out of the docroot directory.
		os.chdir(DOCROOT)

		usehost = self.config.get("setup", "usehostname")

		# Thank to http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib for the IP tips.
		if usehost == False:
			IP = socket.gethostbyname(socket.getfqdn())
		else:
			IP = socket.gethostbyname(socket.gethostname())

		try:
			# Set up the http handler. This does the "grunt" work. The more fine grained details are handled in the SSPHTTPHandler class.
			Handler = SSPHTTPHandler

			# This creates a tcp server using the Handler. As I understand it, this creates a standard TCP server and then handles connections to it using the SSPHTTPHandler class.
			httpd = SocketServer.TCPServer(("", PORT), Handler)

			# Print the version of ssp.
			print("=> ssp/" + SSP_VERSION + " running on " + PLAT)

			# Print the port that the server will pipe content through.
			print("	==> Serving on port " + str(PORT))

			# Print the IP address of the server.
			print("	==> Serving on IP " + str(IP))

			# If the document root config option is set to ., serve content out of the current working directory.
			if DOCROOT == ".":
				print("	==> Serving out of " + os.getcwd())
			else:
				print("	==> Serving out of " + DOCROOT)

			print("\nLog:")

			# Serve content "forever" until a KeyBoardInterrupt is issued (Control-C).
			httpd.serve_forever()
		except KeyboardInterrupt:
			# self.statsDB.close()
			# If Control-C is pressed, kill the server.
			sys.exit(0)

if __name__ == "__main__":
	s = sspserver()
