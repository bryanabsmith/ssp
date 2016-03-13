#!/usr/bin/python

"""
    theatre statistics reporter.
"""

import dbm
import configparser
import sys
import time

"""
    This is the stats module which helps to generate
    and report back stats about the server.
"""

class THEATREStats(object):
    """
        THEATREStats module - the "workhorse" module.
    """
    config = configparser.RawConfigParser(allow_no_value=True)

    """
        Statistics class for THEATRE - init.
    """
    def __init__(self):

        self.config.read("theatre.config")

        #stats_db_location = self.config.get("stats", "location")
        try:
            stats_db = dbm.open("{}/theatre_stats".format(self.config.get("stats", "location")), "c")
        except IOError:
            print((" :: It would appear as though the [stats] -> " + \
                  "location configuration option is set to a location " + \
                  "that isn't a valid directory. Please set it to a " +
                  "valid directory and re-execute theatre_stats."))
            sys.exit(0)

        #show_daily = self.config.get("stats", "show_daily_requests")

        #visualize_bars = ""

        date_time = {
            "notformatted": time.strftime("%H-%M-%S_%d-%m-%Y"),
            "formatted": time.strftime("%d/%m/%Y, %H:%M:%S")
        }
        try:
            #option = sys.argv[1]
            if sys.argv[1] == "export_csv":
                output = "key, value\n"
                for keys in sorted(stats_db.keys()):
                    output += "%s, %s\n" % (keys.decode("utf-8"), stats_db[keys].decode("utf-8"))
                output_csv = open("%s/theatre_csv_%s.csv" %
                                  (self.config.get("stats", "output_csv"),
                                   date_time["notformatted"]), "w")
                output_csv.write(output)
                output_csv.close()
                print((" :: Statistics exported to %s/theatre_csv_%s.csv" %
                      (self.config.get("stats", "output_csv"), date_time["notformatted"])))
            elif sys.argv[1] == "export_html":
                
                totals = {
                    "browsers": 0,
                    "oses": 0,
                    "requests": 0
                }

                counts = {
                    "browsers": [],
                    "browsers_value": [],
                    "oses": [],
                    "oses_value": [],
                    "requests": [],
                    "requests_value": []
                }

                for keys in list(stats_db.keys()):
                    if keys[:7].decode("utf-8") == "browser":
                        totals["browsers"] += int(stats_db[keys])
                    elif keys[:2].decode("utf-8") == "os":
                        totals["oses"] += int(stats_db[keys])
                    elif keys.decode("utf-8") == "requests":
                        totals["requests"] = stats_db["requests"]

                for keys in sorted(stats_db.keys()):
                    if keys[:7].decode("utf-8") == "browser":
                        counts["browsers"].append(keys[8:].decode("utf-8").replace("_", " ") +
                                                  " (%s, %s%%)" %
                                                  (stats_db[keys].decode("utf-8"),
                                                   str(round((float(
                                                       stats_db[keys])/totals["browsers"])
                                                             *100, 2))))
                        counts["browsers_value"].append(int(stats_db[keys]))
                    elif keys[:2].decode("utf-8") == "os":
                        counts["oses"].append(keys[3:].decode("utf-8").replace("_", " ") +
                                              " (%s, %s%%)" %
                                              (stats_db[keys].decode("utf-8"),
                                               str(round((float(stats_db[keys])/totals["oses"])
                                                         *100, 2))))
                        counts["oses_value"].append(int(stats_db[keys]))
                    elif keys[:9].decode("utf-8") == "requests_":
                        counts["requests"].append(keys[9:].decode("utf-8").replace("_", "/"))
                        counts["requests_value"].append(int(stats_db[keys]))
                #requests_max = max(requests_value) + 2
                stats_html = """
                    <html>
                      <head>
                        <link rel='stylesheet' href='http://cdn.jsdelivr.net/chartist.js/latest/chartist.min.css'>
                        <link href='https://fonts.googleapis.com/css?family=Raleway' rel='stylesheet' type='text/css'>
                        <script src='http://cdn.jsdelivr.net/chartist.js/latest/chartist.min.js'></script>
                        <style>body {background-color: #F2F2F0; font-family: 'Raleway', sans-serif; margin: 5%%;}</style>
                      </head>
                      <body>
                        <h1>theatre Statistics (%s)</h1>
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
                       totals["requests"].decode("utf-8"),
                       counts["browsers"],
                       counts["browsers_value"],
                       counts["oses"],
                       counts["oses_value"],
                       counts["requests"],
                       counts["requests_value"],
                       int(max(counts["requests_value"]) + 2))

                f_output = open("%s/theatre_html_%s.html" %
                                (self.config.get("stats", "output_html"),
                                 date_time["notformatted"]), "w")
                f_output.writelines(stats_html)
                f_output.close()
                print((" :: Statistics exported to %s/theatre_html_%s.html" %
                      (self.config.get("stats", "output_html"), date_time["notformatted"])))
            else:
                print(" :: Invalid option. Possible options:\n     "
                      ":: export_csv - Export the keys and values to a csv file.\n     "
                      ":: export_html - Export the keys and values to a html file.")
        except IndexError:
            try:
                for keys in sorted(stats_db.keys()):
                    if self.config.get("stats", "show_daily_requests") == "False":
                        if keys[:8] == "requests":
                            pass
                        else:
                            print(" :: %s=%s" % (keys.decode("utf-8"), stats_db[keys].decode("utf-8")))
                    else:
                        print(" :: %s=%s" % (keys.decode("utf-8"), stats_db[keys].decode("utf-8")))
            except KeyError:
                print(":: No data.")
        #except ValueError:
            #print(":: No data.")

    @staticmethod
    def get_server_version():
        """
            Return server version.
        """
        import theatre
        return theatre.__theatre_version__

    @staticmethod
    def get_server_platform():
        """
            Return server platform.
        """
        import theatre
        return theatre.__plat__

if __name__ == "__main__":
    THEATRE_STATS = THEATREStats()
