#!/usr/bin/env python

"""
    ssp main script.
"""

from __future__ import print_function

import anydbm
import ConfigParser
import datetime
import logging
import os
import platform
import SimpleHTTPServer
import SocketServer
import socket
import subprocess
import sys
import time

import httpagentparser
import netifaces

__port__ = 8888
__ssp_version__ = "0.1"
__docroot__ = "."
__itworks__ = "html/index.html"
__logfile__ = "ssp.log"
__ip__ = "0.0.0.0"
__plat__ = sys.platform


"""
    This is the "workhorse" module - the server itself.
    It's made up of two classes:
        - SSPHTTPHandler - the handler for the server requests itself.
        - SSPServer - this basically starts the server and then
            defers to SSPHTTPHandler for everything else.
"""

# http://stackoverflow.com/a/25375077
class SSPHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
        The handler class, handles requests, writing output and authentication.
    """

    # Set the server version
    SimpleHTTPServer.SimpleHTTPRequestHandler.server_version = __ssp_version__

    # ConfigParser for the Handler class
    config = ConfigParser.SafeConfigParser(allow_no_value=True)

    def log_message(self, format, *args):
        __detailed__ = self.config.get("setup", "detailed")

        # The codes are stored in the second argument of the args array that includes
        # response log messages.
        code = args[1]
        # 200 is OK - this is what we're looking for.

        http_codes = {"100": "Continue",
                      "101": "Switching Protocols",
                      "200": "OK",
                      "201": "Created",
                      "202": "Accepted",
                      "203": "Non-Authoritative Information",
                      "204": "No Content",
                      "205": "Reset Content",
                      "206": "Partial Content",
                      "300": "Multiple Choices",
                      "301": "Moved Permanently",
                      "302": "Found",
                      "303": "See Other",
                      "304": "Not Modified",
                      "305": "Use Proxy",
                      "307": "Temporary Redirect",
                      "400": "Bad Request",
                      "401": "Unauthorized",
                      "402": "Payment Required",
                      "403": "Forbidden",
                      "404": "Not Found",
                      "405": "Method Not Allowed",
                      "406": "Not Acceptable",
                      "407": "Proxy Authentication Required",
                      "408": "Request Timeout",
                      "409": "Conflict",
                      "410": "Gone",
                      "411": "Length Required",
                      "412": "Precondition Failed",
                      "413": "Request Entity Too Large",
                      "414": "Request-URI Too Long",
                      "415": "Unsupported Media Type",
                      "416": "Requested Range Not Satisfiable",
                      "417": "Expectation Failed",
                      "500": "Internal Server Error",
                      "501": "Not Implemented",
                      "502": "Bad Gateway",
                      "503": "Service Unavailable",
                      "504": "Gateway Timeout",
                      "505": "HTTP Version Not Supported"}

        # Check to see if the user wants detailed logging.
        if __detailed__ == "True":
            if __plat__ == "win32":
                print("[RQ] (%s): %s ==> %s" %
                      (self.log_date_time_string(), self.client_address[0], format % args))
            else:
                # Print log messages based on the response code.
                # Each time a request is sent to the server, it responds with a three digit code.
                print("\033[0;32;49m[RQ]\033[0m (%s): %s ==> %s" % (
                    self.log_date_time_string(), self.client_address[0], format % args))
            logging.info("[RQ] (%s): %s ==> %s" %
                         (self.log_date_time_string(), self.client_address[0], format % args))
        else:
            # if code == "200":
            # code = "OK (200)"
            if __plat__ == "win32":
                print("[RQ] (%s): GET %s, %s (%s)" %
                      (self.log_date_time_string(), self.path, code, http_codes[code]))
            else:
                print("\033[1;32;49m[RQ]\033[0m (%s): GET %s, %s (%s)" % (
                    self.log_date_time_string(), self.path, code, http_codes[code]))

    def get_os(self):
        """
            Returns the operating system that ssp is running on.
        """
        platform_name = platform.system()
        if platform_name == "Darwin":
            return "OS X %s" % platform.mac_ver()[0]
        elif platform_name == "Windows":
            # http://www.deepakg.com/blog/2007/08/using-wmic-for-gathering-system-info/
            plat_name = subprocess.Popen("wmic os get name", stdout=subprocess.PIPE, shell=True)
            win_os = plat_name.stdout.readlines()[1]
            win_os = win_os.split("|")
            # platform_name = "Windows %s" % platform.win32_ver()[0]
            return win_os[0]
        elif platform_name == "Linux":
            return "%s Linux (%s)" % \
                   (platform.linux_distribution()[0].capitalize(), platform.release())
        elif platform_name == "FreeBSD":
            return "%s (%s)" % (platform_name, platform.release())
        else:
            return platform_name

    def show_server_status(self):
        """
            Writes out the status of the server if user navigates to /sysinfo/(<key>).
        """
        try:
            import psutil

            stats_db_location = self.config.get("stats", "location")
            stats_db = anydbm.open("%s/ssp_stats.db" % stats_db_location, "c")

            # https://github.com/giampaolo/psutil
            mem = (psutil.virtual_memory()[0] / 1024) / 1024
            cpu = psutil.cpu_times_percent(interval=1, percpu=False)
            cpu_user = cpu[0]
            cpu_system = cpu[2]
            cpu_idle = cpu[3]
            # This only gets the first partition for now.
            disk = psutil.disk_usage(psutil.disk_partitions()[0][1])
            disk_total = ((disk[0] / 1024) / 1024) / 1024
            nic = self.config.get("setup", "nix_interface")
            nic_info = psutil.net_io_counters(pernic=True)[nic]
            request_count = str(stats_db["requests"])

            log = open(__logfile__, "r")
            log_contents = ""
            for line in reversed(log.readlines()):
                log_contents += r"%s<br \>" % line
            log.close()

            # http://www.w3.org/TR/WCAG20-TECHS/H76.html - Meta refresh
            self.wfile.write(r"""
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
                             % (self.get_os(), str(mem), cpu_user,
                                cpu_system, cpu_idle, disk_total, str(nic_info[0]),
                                str(nic_info[1]), str(nic_info[2]),
                                str(nic_info[3]), request_count, log_contents))
        except ImportError:
            self.wfile.write(
                """<h5>psutil module not installed.
                Please install this first before attempting to see system info.""")

    def do_authhead(self):
        """
            Send authentication headers to end user.
        """
        # Load the configuration file.
        self.config.read("ssp.config")

        stats_db_location = self.config.get("stats", "location")
        stats_db = anydbm.open("%s/ssp_stats.db" % stats_db_location, "c")

        #auth_key = self.config.get("auth", "auth_key")

        auth_msg = self.config.get("auth", "auth_box_message")

        self.send_response(401)

        #self.send_header("WWW-Authenticate", "Basic %s" % auth_key)
        self.send_header(r"WWW-Authenticate", "Basic realm=\"%s\"" % auth_msg)
        self.send_header("Content-type", "text/html")

        # http://b.leppoc.net/2010/02/12/simple-webserver-in-python/
        headers = self.headers.getheader("User-Agent")
        # print(libuasparser.browser_search(headers))
        # http://shon.github.io/httpagentparser/
        simpleheaders = httpagentparser.simple_detect(headers)
        # print(simpleheaders)

        os_header = str(simpleheaders[0].replace(" ", "_"))
        browser_header = str(simpleheaders[1].replace(" ", "_"))

        try:
            stats_db["os_%s" % os_header] = str(int(stats_db["os_%s" % os_header]) + 1)
        except KeyError:
            stats_db["os_%s" % os_header] = "1"

        try:
            stats_db["browser_%s" % browser_header] = \
                str(int(stats_db["browser_%s" % browser_header]) + 1)
        except KeyError:
            stats_db["browser_%s" % browser_header] = "1"

        __clientinfo__ = self.config.get("setup", "clientInfo")

        # Check to see if the user wants detailed logging.
        if __clientinfo__ == "True":
            if __plat__ == "win32":
                c_info = "	[CL] %s, %s" % \
                        (os_header.replace("_", " "), browser_header.replace("_", " "))
            else:
                c_info = r"	\033[0;36;49m[CL]\033[0m %s, %s" % (
                    os_header.replace("_", " "), browser_header.replace("_", " "))
            print(c_info)
            logging.info("	[CL] %s, %s" %
                         (os_header.replace("_", " "), browser_header.replace("_", " ")))

        # End the headers.
        self.end_headers()
        #self.write_get()

    # https://wiki.python.org/moin/BaseHttpServer
    def do_head(self):
        """
            Send headers to end user.
        """
        # Load the configuration file.
        self.config.read("ssp.config")

        stats_db_location = self.config.get("stats", "location")
        stats_db = anydbm.open("%s/ssp_stats.db" % stats_db_location, "c")

        self.send_response(200)

        # Set the content to html.
        self.send_header("Content-type", "text/html; charset=utf-8")

        # http://b.leppoc.net/2010/02/12/simple-webserver-in-python/
        headers = self.headers.getheader("User-Agent")
        # print(libuasparser.browser_search(headers))
        # http://shon.github.io/httpagentparser/
        simpleheaders = httpagentparser.simple_detect(headers)
        # print(simpleheaders)

        os_header = str(simpleheaders[0].replace(" ", "_"))
        browser_header = str(simpleheaders[1].replace(" ", "_"))

        try:
            stats_db["os_%s" % os_header] = str(int(stats_db["os_%s" % os_header]) + 1)
        except KeyError:
            stats_db["os_%s" % os_header] = "1"

        try:
            stats_db["browser_%s" % browser_header] = \
                str(int(stats_db["browser_%s" % browser_header]) + 1)
        except KeyError:
            stats_db["browser_%s" % browser_header] = "1"

        __clientinfo__ = self.config.get("setup", "clientInfo")

        # Check to see if the user wants detailed logging.
        if __clientinfo__ == "True":
            if __plat__ == "win32":
                c_info = "	[CL] %s, %s" % \
                        (os_header.replace("_", " "), browser_header.replace("_", " "))
            else:
                c_info = r"	\033[0;36;49m[CL]\033[0m %s, %s" % (
                    os_header.replace("_", " "), browser_header.replace("_", " "))
            print(c_info)
            logging.info("	[CL] %s, %s" %
                         (os_header.replace("_", " "), browser_header.replace("_", " ")))
        # End the headers.
        self.end_headers()
        #self.write_get()

    # https://wiki.python.org/moin/BaseHttpServer
    def do_GET(self):
        """
            Check to see if you need to authenticate or not
        """
        self.config.read("ssp.config")
        auth_enabled = self.config.get("auth", "auth_enabled")
        auth_key = self.config.get("auth", "auth_key")

        # https://gist.github.com/fxsjy/5465353
        if auth_enabled == "True":
            if self.headers.getheader("Authorization") is None:
                self.do_authhead()
                # self.wfile.write("Password not accepted.")
                pass
            elif self.headers.getheader("Authorization") == "Basic %s" % auth_key:
                self.write_get()
                pass
            else:
                self.do_authhead()
                print("""	\033[0;35;49m[__ip__]\033[0m
                        Incorrect password entered during authentication.""")
                pass
                # print("Not authenticated.") # Mistaken password
        else:
            # Create the headers.
            self.do_head()

    def write_get(self):
        """
            Write the page requested by the end user.
        """
        # Necessary for Firefox if auth is set to True.
        # Otherwise, it renders the page as plain text.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Server", "ssp/%s" % __ssp_version__)
        self.end_headers()

        # Load the configuration file.
        self.config.read("ssp.config")

        # print(self.address_string())

        # "It Works" page.
        # itworks = self.config.get("content", "itworks")

        docroot_dir = self.config.get("content", "docroot")

        platform_name = str(self.get_os())

        # Log that headers were sent
        logging.info("headers")

        redirect_value = self.config.get("redirect", "redirect")
        redirect_url = self.config.get("redirect", "url")
        redirect_timeout = self.config.getint("redirect", "timeout")
        status_enabled = self.config.get("server", "status")
        status_complex = self.config.get("server", "complex_status")
        status_complex_path = self.config.get("server", "complex_status_path")

        if redirect_value == "True":
            self.wfile.write("<h4>Page has moved. Redirecting in %s seconds...</h4>" %
                             str(redirect_timeout))
            time.sleep(redirect_timeout)
            # https://css-tricks.com/redirect-web-page/
            self.wfile.write(r"<meta http-equiv=\"refresh\" content=\"0; URL='%s'\" />" %
                             redirect_url)
        elif self.path[:8] == "/sysinfo":
            if status_enabled == "True":
                if status_complex == "True":
                    if self.path == "/sysinfo/%s/" % status_complex_path:
                        self.show_server_status()
                    else:
                        self.wfile.write("Access denied.")
                else:
                    self.show_server_status()
            else:
                self.wfile.write("Access denied.")
        else:
            if self.path == "/":
                # Check to see if an index.html or index.htm already exists.
                # If it doesn't, use one set by the user in the config file.
                if os.path.isfile("%s/index.html" % docroot_dir) is False:
                    # This loads the default index file that the user configures.
                    try:
                        default_page = open("webroot/default_index.html", "r")
                        page = default_page.read()
                        page = page.replace("&version&", __ssp_version__)
                        page = page.replace("&webroot&", docroot_dir)
                        page = page.replace("&platform&", platform_name)
                        self.wfile.write(page)
                        default_page.close()
                    except IOError as err:
                        print("	=> Error: %s (%s)" % (err.strerror, self.path))
                        #logging.error("Error: %s (%s)" % (err.strerror, self.path))
                        logging.error("Error: %s (%s)", (err.strerror, self.path), None)
                # If there is an index.html available, use that.
                elif os.path.isfile("%s/index.html" % docroot_dir) is True:
                    f_index = open("%s/index.html" % docroot_dir, "r")
                    poweredby = self.config.get("content", "poweredby")
                    if poweredby == "true":
                        self.wfile.write(
                            f_index.read() + r"""<p style='font-family: \"Arial\";
                             font-size: 10pt; text-align: center;'>
                             <span>Powered by ssp/%s.</span></p>""" % __ssp_version__)
                    else:
                        self.wfile.write(f_index.read())
                    f_index.close()
            else:
                try:
                    # https://wiki.python.org/moin/BaseHttpServer
                    f_index = open("%s/%s" % (docroot_dir, self.path[1:]), "r")
                    self.wfile.write(f_index.read())
                    f_index.close()
                except IOError as err:
                    if self.path != "/favicon.ico":
                        if err.strerror == "Is a directory":
                            try:
                                f_index = open("%sindex.html" % self.path[1:], "r")
                                poweredby = self.config.get("content", "poweredby")
                                if poweredby == "true":
                                    self.wfile.write(
                                        f_index.read() + r"""<p style='font-family: \"Arial\";
                                         font-size: 10pt; text-align: center;'>
                                         <span>Powered by ssp/%s.</span></p>""" % __ssp_version__)
                                else:
                                    self.wfile.write(f_index.read())
                                f_index.close()
                            except IOError:
                                print("	=> Error: %s (%s)" % (err.strerror, self.path))
                                logging.error("Error: %s (%s)", (err.strerror, self.path), None)

                                page404 = self.config.get("content", "custom404")
                                f_index = open(page404, "r")
                                poweredby = self.config.get("content", "poweredby")
                                if poweredby == "true":
                                    self.wfile.write(
                                        f_index.read() + r"""<p style='font-family: \"Arial\";
                                         font-size: 10pt; text-align: center;'>
                                         <span>Powered by ssp/%s.</span></p>""" % __ssp_version__)
                                else:
                                    self.wfile.write(f_index.read())
                                f_index.close()
                        else:
                            if __plat__ == "win32":
                                print("	[ER] %s (%s)" % (err.strerror, self.path))
                            else:
                                print(r"	\033[0;31;49m[ER]\033[0m %s (%s)" %
                                      (err.strerror, self.path))
                            logging.error("Error: %s (%s)", (err.strerror, self.path), None)
                            page404 = self.config.get("content", "custom404")
                            f_index = open(page404, "r")
                            self.wfile.write(f_index.read())
                            f_index.close()

        # x = open("/Users/vansmith/index.html", "r")
        # self.wfile.write(x.read())
        # x.close()

        # Open up the stats database.
        stats_db_location = self.config.get("stats", "location")
        stats_db = anydbm.open("%s/ssp_stats.db" % stats_db_location, "c")

        # Add a value to the total requests
        try:
            stats_db["requests"] = str(int(stats_db["requests"]) + 1)
        except KeyError:
            stats_db["requests"] = "1"

        try:
            year = datetime.datetime.now().year
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day
            stats_db["requests_%s_%s_%s" % (year, month, day)] = str(
                int(stats_db["requests_%s_%s_%s" % (year, month, day)]) + 1)
        except KeyError:
            stats_db["requests_%s_%s_%s" % (year, month, day)] = "1"


class SSPServer(object):
    """
        The primary class, sets up the server and handler for requests.
    """
    def __init__(self):
        """
            Constructor for main server class.
        """

        start_time = time.time()

        # Setup the configuration parser.
        self.config = ConfigParser.RawConfigParser(allow_no_value=True)

        # OS X config location
        # These are all the same for now (planning for platform specific paths).
        if __plat__ == "darwin":
            self.config.read("ssp.config")
        # Windows config location
        elif __plat__ == "win32":
            self.config.read("ssp.config")
        # Linux config location
        elif __plat__.find("linux") > -1:
            self.config.read("ssp.config")
        # Everything else config location
        else:
            self.config.read("ssp.config")

        # Set the log file.
        __logfile__ = self.config.get("setup", "logfile")

        # Setup the logger.
        # http://stackoverflow.com/q/11581794 - formatting help
        self.logger = logging.basicConfig(filename=__logfile__, level=logging.DEBUG,
                                          format="[%(asctime)s]: %(levelname)s: %(message)s")

        # Log that things got started
        logging.info("ssp started.")

        # Set the port based on the config file.
        __port__ = int(self.config.get("setup", "port"))

        # Set the version based on the config file.
        # __ssp_version__ = "ssp/" + self.config.get("setup", "ssp_version")

        # Set the docroot based on the config file.
        __docroot__ = self.config.get("content", "docroot")

        # Set the location of the "It Works" page (the default index.html page).
        # This is now written into the server itself for the purposes of simplifying things.
        # __itworks__ = self.config.get("content", "itworks")

        # Change the working directory to the one specified for the docroot.
        # This ensures that we are serving content out of the docroot directory.
        # os.chdir(__docroot__)

        use_host = self.config.get("setup", "usehostname")
        use_nix_complex = self.config.get("setup", "use_nix_ip_workaround")
        # linuxOutbound = self.config.get("setup", "use_linux_ip_outbond_test")
        # useFreeBSDComplex = self.config.get("setup", "use_freebsd_ip_workaround")

        __ip__ = "0.0.0.0"

        use_external_ip = self.config.get("setup", "use_external_ip")

        if use_external_ip == "True":
            # http://myexternalip.com/#python-request
            external_url = "http://www.myexternalip.com/raw"
            import requests
            req = requests.get(external_url)
            __ip__ = req.text.strip("\n")
        else:
            if use_nix_complex == "True":
                interface = self.config.get("setup", "nix_interface")
                try:
                    __ip__ = netifaces.ifaddresses(interface)[2][0]["addr"]
                except ValueError:
                    print("""It would appear that the interface that
                     you've set for nix_interface is incorrect.
                     Please double check and try launching ssp again.""")
            else:
                try:
                    # Thank to http://stackoverflow.com/questions/166506/
                    # finding-local-ip-addresses-using-pythons-stdlib for the __ip__ tips.
                    if use_host == "False":
                        __ip__ = socket.gethostbyname(socket.getfqdn())
                    else:
                        __ip__ = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    __ip__ = "ERROR GETTING __ip__"

        try:
            # Set up the http handler. This does the "grunt" work.
            # The more fine grained details are handled in the SSPHTTPHandler class.
            handler = SSPHTTPHandler

            try:
                # This creates a tcp server using the Handler.
                # As I understand it, this creates a standard TCP server
                # and then handles connections to it using the SSPHTTPHandler
                # class.
                httpd = SocketServer.TCPServer(("", __port__), handler)

                if __plat__ == "win32":
                    print("ssp/%s\n[Host]    http://%s:%s\n[WebRoot] %s" %
                          (__ssp_version__, str(__ip__), str(__port__), __docroot__))
                else:
                    print("ssp/%s\n\033[0;33;49m[Host]\033[0m    http://" \
                          "%s:%s\n\033[0;33;49m[WebRoot]\033[0m %s" %
                          (__ssp_version__, str(__ip__), str(__port__), __docroot__))

                print("\nLog:")

                # https://forum.omz-software.com/topic/584/stopping-simplehttpserver/2
                # and https://docs.python.org/2/library/basehttpserver.html#more-examples
                httpd.serve_forever()
            except socket.error:
                print("Socket in use on this port. Clear the socket and try again.")
                # http://stackoverflow.com/questions/12397175/how-do-i-close-an-open-port-from-the-terminal-on-the-mac
                print("	On a Unix system, execute the following:")
                print("		sudo lsof -i :<__port__ NUMBER>")
                print("		sudo kill -9 <PID>")

        except KeyboardInterrupt:

            # self.stats_db.close()
            # http://stackoverflow.com/a/1557584
            run_time = time.time() - start_time

            # http://stackoverflow.com/a/775075
            minutes, seconds = divmod(run_time, 60)
            hours, minutes = divmod(minutes, 60)
            run_time = "Run Time: %d:%02d:%02d" % (hours, minutes, seconds)
            if __plat__ == "win32":
                print("\rClosing ssp...\n%s" % run_time)
            else:
                print("\r\033[0;35;49mClosing ssp...\n%s\033[0m" % run_time)
            logging.info(run_time)
            # If Control-C is pressed, kill the server.
            sys.exit(0)


if __name__ == "__main__":
    SSP_SERVER = SSPServer()
