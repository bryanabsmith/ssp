#!/usr/bin/python

"""
    ssp statistics reporter.
"""

import anydbm
import ConfigParser
import sys
import time

"""
    This is the stats module which helps to generate
    and report back stats about the server.
"""

class SSPStats(object):
    """
        SSPStats module - the "workhorse" module.
    """
    config = ConfigParser.RawConfigParser(allow_no_value=True)

    """
        Statistics class for SSP - init.
    """
    def __init__(self):

        self.config.read("ssp.config")

        stats_db_location = self.config.get("stats", "location")
        try:
            stats_db = anydbm.open("%s/ssp_stats.db" % stats_db_location, "c")
        except IOError:
            print(" :: It would appear as though the [stats] -> " + \
                  "location configuration option is set to a location " + \
                  "that isn't a valid directory. Please set it to a " +
                  "valid directory and re-execute ssp_stats.")
            sys.exit(0)

        show_daily = self.config.get("stats", "show_daily_requests")

        #visualize_bars = ""

        date_time = {
            "notformatted": time.strftime("%H-%M-%S_%d-%m-%Y"),
            "formatted": time.strftime("%d/%m/%Y, %H:%M:%S")
        }
        #date_time = time.strftime("%H-%M-%S_%d-%m-%Y")
        #nice_date_time = time.strftime("%d/%m/%Y, %H:%M:%S")

        # http://www.tutorialspoint.com/python/python_command_line_arguments.htm
        # if sys.argv[1] == "reset":
            # opt = raw_input(":: Are you sure that you want to reset the statistics (y/n)? ")
            # if opt == "y" or opt == "yes":
                # http://stackoverflow.com/a/16649789
                # for key, v in stats_db.iteritems():
                    # del stats_db[key]
                    # print(key)
        # else:
        print ":: Statistics for ssp"
        try:
            #option = sys.argv[1]
            if sys.argv[1] == "export_csv":
                output = "key, value\n"
                for keys in sorted(stats_db.keys()):
                    output += "%s, %s\n" % (keys, stats_db[keys])
                output_csv = open("%s/ssp_csv_%s.csv" %
                                  (self.config.get("stats", "output_csv"),
                                   date_time["notformatted"]), "w")
                output_csv.write(output)
                output_csv.close()
                print(" :: Statistics exported to %s/ssp_csv_%s.csv" %
                      (self.config.get("stats", "output_csv"), date_time["notformatted"]))
            elif sys.argv[1] == "export_html":
                totals = {
                    "browsers": 0,
                    "oses": 0,
                    "requests": 0
                }
                browsers = []
                browsers_value = []
                #browsers_total = 0
                oses = []
                oses_value = []
                #oses_total = 0
                requests = []
                requests_value = []
                #requests_max = 0
                #requests_total = 0

                for keys in stats_db.keys():
                    if keys[:7] == "browser":
                        totals["browsers"] += int(stats_db[keys])
                    elif keys[:2] == "os":
                        totals["oses"] += int(stats_db[keys])
                    elif keys == "requests":
                        totals["requests"] = stats_db["requests"]

                for keys in sorted(stats_db.keys()):
                    if keys[:7] == "browser":
                        browsers.append(keys[8:].replace("_", " ") +
                                        " (%s, %s%%)" %
                                        (stats_db[keys],
                                         str(round((float(
                                             stats_db[keys])/totals["browsers"])*100, 2))))
                        browsers_value.append(int(stats_db[keys]))
                    elif keys[:2] == "os":
                        oses.append(keys[3:].replace("_", " ") +
                                    " (%s, %s%%)" %
                                    (stats_db[keys],
                                     str(round((float(stats_db[keys])/totals["oses"])*100, 2))))
                        oses_value.append(int(stats_db[keys]))
                    elif keys[:9] == "requests_":
                        requests.append(keys[9:].replace("_", "/"))
                        requests_value.append(int(stats_db[keys]))
                requests_max = max(requests_value) + 2

                stats_html = """
                    <html>
                      <head>
                        <link rel='stylesheet' href='http://cdn.jsdelivr.net/chartist.js/latest/chartist.min.css'>
                        <link href='https://fonts.googleapis.com/css?family=Raleway' rel='stylesheet' type='text/css'>
                        <script src='http://cdn.jsdelivr.net/chartist.js/latest/chartist.min.js'></script>
                        <style>body {background-color: #F2F2F0; font-family: 'Raleway', sans-serif; margin: 5%%;}</style>
                      </head>
                      <body>
                        <h1>ssp Statistics (%s)</h1>
                        <h3>Browser</h3><div id='chartBrowser' class='ct-chart ct-perfect-fourth'></div><p></p>
                        <h3>Operating Systems</h3><div id='chartOS' class='ct-chart ct-perfect-fourth'></div><p></p>
                        <h3>Requests (%s total)</h3><div id='chartRequests' class='ct-chart ct-perfect-fourth'></div>
                        <script>
                          new Chartist.Pie('#chartBrowser', {labels: %s, series: %s}, {donut: true, donutWidth: 50, startAngle: 0, total: 0, showLabel: true, chartPadding: 100, labelOffset: 50, labelDirection: 'explode'});
                          new Chartist.Pie('#chartOS', {labels: %s, series: %s}, {donut: true, donutWidth: 50, startAngle: 0, total: 0, showLabel: true, chartPadding: 100, labelOffset: 50, labelDirection: 'explode'});
                          new Chartist.Line('#chartRequests', {labels: %s, series: [%s]}, {high: %i, low: 0, showArea: true});
                        </script>
                      </body>
                    </html>
                """ % (date_time["formatted"],
                       totals["requests"],
                       browsers,
                       browsers_value,
                       oses,
                       oses_value,
                       requests,
                       requests_value,
                       int(requests_max))

                f_output = open("%s/ssp_html_%s.html" %
                                (self.config.get("stats", "output_html"),
                                 date_time["notformatted"]), "w")
                f_output.writelines(stats_html)
                f_output.close()
                print(" :: Statistics exported to %s/ssp_html_%s.html" %
                      (self.config.get("stats", "output_html"), date_time["notformatted"]))
            else:
                print(" :: Invalid option. Possible options:\n     "
                      ":: export_csv - Export the keys and values to a csv file.\n     "
                      ":: export_html - Export the keys and values to a html file.")
        except IndexError:
            try:
                for keys in sorted(stats_db.keys()):
                    if show_daily == "False":
                        if keys[:8] == "requests":
                            pass
                        else:
                            print " :: %s=%s" % (keys, stats_db[keys])
                    else:
                        print " :: %s=%s" % (keys, stats_db[keys])
            except KeyError:
                print ":: No data."

    @staticmethod
    def get_server_version():
        """
            Return server version.
        """
        import ssp
        return ssp.__ssp_version__

    @staticmethod
    def get_server_platform():
        """
            Return server platform.
        """
        import ssp
        return ssp.__plat__

if __name__ == "__main__":
    SSP_STATS = SSPStats()
