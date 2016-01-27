#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import anydbm
import ConfigParser
import datetime
import httpagentparser
import logging
import os
import platform
import SimpleHTTPServer
import SocketServer
import socket
import subprocess
import sys
import time

PORT = 8888
SSP_VERSION = "0.1"
DOCROOT = "."
ITWORKS = "html/index.html"
LOGFILE = "ssp.log"
IP = "0.0.0.0"
PLAT = sys.platform


# http://stackoverflow.com/a/25375077
class SSPHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    # Set the server version
    SimpleHTTPServer.SimpleHTTPRequestHandler.server_version = SSP_VERSION

    # ConfigParser for the Handler class
    config = ConfigParser.SafeConfigParser(allow_no_value=True)

    def log_message(self, format, *args):
        DETAILED = self.config.get("setup", "detailed")

        # Check to see if the user wants detailed logging.
        if DETAILED == "True":
            if PLAT == "win32":
                print("[RQ] (%s): %s ==> %s" % (self.log_date_time_string(), self.client_address[0], format%args))
            else:
                # Print log messages based on the response code.
                # Each time a request is sent to the server, it responds with a three digit code.
                print("\033[0;32;49m[RQ]\033[0m (%s): %s ==> %s" % (self.log_date_time_string(), self.client_address[0], format%args))
            logging.info("[RQ] (%s): %s ==> %s" % (self.log_date_time_string(), self.client_address[0], format%args))
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
            if PLAT == "win32":
                print("[RQ] (%s): %s" % (self.log_date_time_string(), httpCodes[code]))
            else:
                print("\033[1;32;49m[RQ]\033[0m (%s): %s" % (self.log_date_time_string(), httpCodes[code]))

    def getOS(self):
        platformName = platform.system()
        if platformName == "Darwin":
            return "OS X %s" % platform.mac_ver()[0]
        elif platformName == "Windows":
            # http://www.deepakg.com/blog/2007/08/using-wmic-for-gathering-system-info/
            platName = subprocess.Popen("wmic os get name", stdout=subprocess.PIPE, shell=True)
            winOS = platName.stdout.readlines()[1]
            winOS = winOS.split("|")
            #platformName = "Windows %s" % platform.win32_ver()[0]
            return winOS[0]
        elif platformName == "Linux":
            return "%s Linux (%s)" % (platform.linux_distribution()[0].capitalize(), platform.release())

    def showServerStatus(self):
        try:
            import psutil

            statsDBLocation = self.config.get("stats", "location")
            statsDB = anydbm.open("%s/ssp_stats.db" % statsDBLocation, "c")

            # https://github.com/giampaolo/psutil
            mem = (psutil.virtual_memory()[0]/1024)/1024
            cpu = psutil.cpu_times_percent(interval=1, percpu=False)
            cpuUser = cpu[0]
            cpuSystem = cpu[2]
            cpuIdle = cpu[3]
            disk = psutil.disk_usage(psutil.disk_partitions()[0][1]) # This only gets the first partition for now.
            diskTotal = ((disk[0]/1024)/1024)/1024
            nic = self.config.get("setup", "nix_interface")
            nicInfo = psutil.net_io_counters(pernic=True)[nic]
            requestCount = str(statsDB["requests"])

            log = open(LOGFILE, "r")
            logContents = ""
            for line in reversed(log.readlines()):
                logContents += "%s<br \>" % line
            log.close()

            # http://www.w3.org/TR/WCAG20-TECHS/H76.html - Meta refresh
            self.wfile.write("""
                <meta http-equiv="refresh" content="5"/>
                <h1>Machine Status</h1>
                OS: %s<br \>
                Memory Total: %s MB<br \>
                CPU: %s%% (User), %s%% (System), %s%% (Idle)<br \>
                Disk Total: %s GB<br \>
                Network Information:
                <!-- http://www.sitepoint.com/forums/showthread.php?128125-How-can-I-remove-initial-space-at-top-of-list -->
                <ul style="margin-top:0;"><li>Bytes Sent: %s</li><li>Bytes Recieved: %s</li><li>Packets Sent: %s</li><li>Packets Recieved: %s</li></ul>
                <h1>Server Status</h1>
                Total Requests: %s<p></p>
                <h3>Log</h3>
                <!-- http://stackoverflow.com/a/9707445 -->
                <div style="overflow-y: scroll; height:300px;">%s</div>"""
                % (self.getOS(), str(mem), cpuUser, cpuSystem, cpuIdle, diskTotal, str(nicInfo[0]), str(nicInfo[1]), str(nicInfo[2]), str(nicInfo[3]), requestCount, logContents))
        except ImportError:
            self.wfile.write("<h5>psutil module not installed. Please install this first before attempting to see system info.")

    def do_AUTHHEAD(self):
        # Load the configuration file.
        self.config.read("ssp.config")

        statsDBLocation = self.config.get("stats", "location")
        statsDB = anydbm.open("%s/ssp_stats.db" % statsDBLocation, "c")

        auth_key = self.config.get("auth", "auth_key")

        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic %s" % auth_key)

        # Set the content to html.
        self.send_header("Content-type", "text/html")

        # http://b.leppoc.net/2010/02/12/simple-webserver-in-python/
        headers = self.headers.getheader("User-Agent")
        #print(libuasparser.browser_search(headers))
        # http://shon.github.io/httpagentparser/
        simpleheaders = httpagentparser.simple_detect(headers)
        #print(simpleheaders)

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

        CLIENTINFO = self.config.get("setup", "clientInfo")

        # Check to see if the user wants detailed logging.
        if CLIENTINFO == "True":
            if PLAT == "win32":
                cInfo = "	[CL] %s, %s" % (osHeader.replace("_", " "), browserHeader.replace("_", " "))
            else:
                cInfo = "	\033[0;36;49m[CL]\033[0m %s, %s" % (osHeader.replace("_", " "), browserHeader.replace("_", " "))
            print(cInfo)
            logging.info("	[CL] %s, %s" % (osHeader.replace("_", " "), browserHeader.replace("_", " ")))
        # End the headers.
        self.end_headers()

    # https://wiki.python.org/moin/BaseHttpServer
    def do_HEAD(self):
        # Load the configuration file.
        self.config.read("ssp.config")

        statsDBLocation = self.config.get("stats", "location")
        statsDB = anydbm.open("%s/ssp_stats.db" % statsDBLocation, "c")

        self.send_response(200)

        # Set the content to html.
        self.send_header("Content-type", "text/html")

        # http://b.leppoc.net/2010/02/12/simple-webserver-in-python/
        headers = self.headers.getheader("User-Agent")
        #print(libuasparser.browser_search(headers))
        # http://shon.github.io/httpagentparser/
        simpleheaders = httpagentparser.simple_detect(headers)
        #print(simpleheaders)

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

        CLIENTINFO = self.config.get("setup", "clientInfo")

        # Check to see if the user wants detailed logging.
        if CLIENTINFO == "True":
            if PLAT == "win32":
                cInfo = "	[CL] %s, %s" % (osHeader.replace("_", " "), browserHeader.replace("_", " "))
            else:
                cInfo = "	\033[0;36;49m[CL]\033[0m %s, %s" % (osHeader.replace("_", " "), browserHeader.replace("_", " "))
            print(cInfo)
            logging.info("	[CL] %s, %s" % (osHeader.replace("_", " "), browserHeader.replace("_", " ")))
        # End the headers.
        self.end_headers()

    # https://wiki.python.org/moin/BaseHttpServer
    def do_GET(self):
        self.config.read("ssp.config")
        auth_enabled = self.config.get("auth", "auth_enabled")
        auth_key = self.config.get("auth", "auth_key")

        # https://gist.github.com/fxsjy/5465353
        if auth_enabled == "True":
            if self.headers.getheader("Authorization") == None:
                self.do_AUTHHEAD()
                #self.wfile.write("Password not accepted.")
            elif self.headers.getheader("Authorization") == "Basic %s" % auth_key:
                self.writeGET()
                print("Password has been accepted.")
            else:
                self.do_AUTHHEAD()
                print("	\033[0;35;49m[IP]\033[0m Incorrect password entered during authentication.")
                #print("Not authenticated.") # Mistaken password
        else:
            # Create the headers.
            self.do_HEAD()

    def writeGET(self):

        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()

        # Load the configuration file.
        self.config.read("ssp.config")

        # print(self.address_string())

        # "It Works" page.
        # itworks = self.config.get("content", "itworks")

        docroot_dir = self.config.get("content", "docroot")

        platformName = self.getOS()

        # Log that headers were sent
        logging.info("headers")

        redirectValue = self.config.get("redirect", "redirect")
        redirectURL = self.config.get("redirect", "url")
        redirectTimeout = self.config.getint("redirect", "timeout")
        status_enabled = self.config.get("server", "status")
        status_complex = self.config.get("server", "complex_status")
        status_complex_path = self.config.get("server", "complex_status_path")

        if redirectValue == "True":
            self.wfile.write("<h4>Page has moved. Redirecting in %s seconds...</h4>" % str(redirectTimeout))
            time.sleep(redirectTimeout)
            # https://css-tricks.com/redirect-web-page/
            self.wfile.write("<meta http-equiv=\"refresh\" content=\"0; URL='%s'\" />" % redirectURL)
        elif self.path[:8] == "/sysinfo":
            if status_enabled == "True":
                if status_complex == "True":
                    if self.path == "/sysinfo/%s/" % status_complex_path:
                        self.showServerStatus()
                    else:
                        self.wfile.write("Access denied.")
                else:
                    self.showServerStatus()
            else:
                self.wfile.write("Access denied.")
        else:
            if self.path == "/":
                # Check to see if an index.html or index.htm already exists. If it doesn't, use one set by the user in the config file.
                if os.path.isfile("%s/index.html" % docroot_dir) == False:
                    # This loads the default index file that the user configures.
                    try:
                        default_page = open("webroot/default_index.html", "r")
                        page = default_page.read()
                        page = page.replace("&version&", SSP_VERSION)
                        page = page.replace("&webroot&", docroot_dir)
                        page = page.replace("&platform&", platformName)
                        self.wfile.write(page)
                        default_page.close()
                    except IOError as e:
                        print("	=> Error: %s (%s)" % (e.strerror, self.path))
                        logging.error("Error: %s (%s)" % (e.strerror, self.path))
                # If there is an index.html available, use that.
                elif os.path.isfile("%s/index.html" % docroot_dir) == True:
                    f = open("%s/index.html" % docroot_dir, "r")
                    poweredby = self.config.get("content", "poweredby")
                    if poweredby == "true":
                        self.wfile.write(f.read() + "<p style='font-family: \"Arial\"; font-size: 10pt; text-align: center;'><span>Powered by ssp/%s.</span></p>" % SSP_VERSION)
                    else:
                        self.wfile.write(f.read())
                    f.close()
            else:
                try:
                    # https://wiki.python.org/moin/BaseHttpServer
                    f = open("%s/%s" % (docroot_dir, self.path[1:]), "r")
                    self.wfile.write(f.read())
                    f.close()
                except IOError as e:
                    if self.path != "/favicon.ico":
                        if e.strerror == "Is a directory":
                            try:
                                f = open("%sindex.html" % self.path[1:], "r")
                                poweredby = self.config.get("content", "poweredby")
                                if poweredby == "true":
                                    self.wfile.write(f.read() + "<p style='font-family: \"Arial\"; font-size: 10pt; text-align: center;'><span>Powered by ssp/%s.</span></p>" % SSP_VERSION)
                                else:
                                    self.wfile.write(f.read())
                                f.close()
                            except IOError:
                                print("	=> Error: %s (%s)" % (e.strerror, self.path))
                                logging.error("Error: %s (%s)" % (e.strerror, self.path))

                                page404 = self.config.get("content", "custom404")
                                f = open(page404, "r")
                                poweredby = self.config.get("content", "poweredby")
                                if poweredby == "true":
                                    self.wfile.write(f.read() + "<p style='font-family: \"Arial\"; font-size: 10pt; text-align: center;'><span>Powered by ssp/%s.</span></p>" % SSP_VERSION)
                                else:
                                    self.wfile.write(f.read())
                                f.close()
                        else:
                            if PLAT == "win32":
                                print("	[ER] %s (%s)" % (e.strerror, self.path))
                            else:
                                print("	\033[0;31;49m[ER]\033[0m %s (%s)" % (e.strerror, self.path))
                            logging.error("Error: %s (%s)" % (e.strerror, self.path))
                            page404 = self.config.get("content", "custom404")
                            f = open(page404, "r")
                            self.wfile.write(f.read())
                            f.close()

        #x = open("/Users/vansmith/index.html", "r")
        #self.wfile.write(x.read())
        #x.close()

        # Open up the stats database.
        statsDBLocation = self.config.get("stats", "location")
        statsDB = anydbm.open("%s/ssp_stats.db" % statsDBLocation, "c")

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

        startTime = time.time()

        # Setup the configuration parser.
        self.config = ConfigParser.RawConfigParser(allow_no_value=True)

        # OS X config location
        # These are all the same for now (planning for platform specific paths).
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
        # os.chdir(DOCROOT)

        usehost = self.config.get("setup", "usehostname")
        useNixComplex = self.config.get("setup", "use_nix_ip_workaround")
        #linuxOutbound = self.config.get("setup", "use_linux_ip_outbond_test")
        #useFreeBSDComplex = self.config.get("setup", "use_freebsd_ip_workaround")

        if platform.system() == "FreeBSD" or PLAT.find("linux") > -1 and useNixComplex == "False":
            print("It appears that you're running on FreeBSD or Linux and don't have 'use_nix_ip_workaround' set to True. Please make sure to set this to True to and set 'nix_interface' to the interface that you're serving off of.\n\n")

        useExternalIP = self.config.get("setup", "useExternalIP")

        if useExternalIP == "True":
            # http://myexternalip.com/#python-request
            externalURL = "http://www.myexternalip.com/raw"
            import requests
            req = requests.get(externalURL)
            IP = req.text.strip("\n")
        else:
            if useNixComplex == "True":
                import netifaces
                interface = self.config.get("setup", "nix_interface")
                try:
                    IP = netifaces.ifaddresses(interface)[2][0]["addr"]
                except ValueError:
                    print("It would appear that the interface that you've set for nix_interface is incorrect. Please double check and try launching ssp again.")
            else:
                try:

                    # Thank to http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib for the IP tips.
                    if usehost == "False":
                        IP = socket.gethostbyname(socket.getfqdn())
                    else:
                        IP = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    IP = "ERROR GETTING IP"

        try:
            # Set up the http handler. This does the "grunt" work. The more fine grained details are handled in the SSPHTTPHandler class.
            Handler = SSPHTTPHandler

            try:
                # This creates a tcp server using the Handler. As I understand it, this creates a standard TCP server and then handles connections to it using the SSPHTTPHandler class.
                httpd = SocketServer.TCPServer(("", PORT), Handler)
                '''
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
                '''
                if PLAT == "win32":
                    print("ssp/%s\n[Host]    http://%s:%s\n[WebRoot] %s" % (SSP_VERSION, str(IP), str(PORT), DOCROOT))
                else:
                    print("ssp/%s\n\033[0;33;49m[Host]\033[0m    http://%s:%s\n\033[0;33;49m[WebRoot]\033[0m %s" % (SSP_VERSION, str(IP), str(PORT), DOCROOT))

                print("\nLog:")

                # https://forum.omz-software.com/topic/584/stopping-simplehttpserver/2 and https://docs.python.org/2/library/basehttpserver.html#more-examples
                httpd.serve_forever()
            except socket.error:
                print("Socket in use on this port. Clear the socket and try again.")
                # http://stackoverflow.com/questions/12397175/how-do-i-close-an-open-port-from-the-terminal-on-the-mac
                print("	On a Unix system, execute the following:")
                print("		sudo lsof -i :<PORT NUMBER>")
                print("		sudo kill -9 <PID>")

        except KeyboardInterrupt:

            # self.statsDB.close()
            # http://stackoverflow.com/a/1557584
            runTime = time.time() - startTime

            # http://stackoverflow.com/a/775075
            minutes, seconds = divmod(runTime, 60)
            hours, minutes = divmod(minutes, 60)
            runTime = "Run Time: %d:%02d:%02d" % (hours, minutes, seconds)
            if PLAT == "win32":
                print("\rClosing ssp...\n%s" % runTime)
            else:
                print("\r\033[0;35;49mClosing ssp...\n%s\033[0m" % runTime)
            logging.info(runTime)
            # If Control-C is pressed, kill the server.
            sys.exit(0)

if __name__ == "__main__":
    s = sspserver()