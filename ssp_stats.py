# TO DO: reset stats

import anydbm
import ConfigParser
import sys
import time

class ssp_stats():

    config = ConfigParser.RawConfigParser(allow_no_value=True)

    def __init__(self):

        self.config.read("ssp.config")

        statsDBLocation = self.config.get("stats", "location")
        try:
            statsDB = anydbm.open("%s/ssp_stats.db" % statsDBLocation, "c")
        except:
            print(" :: It would appear as though the [stats] -> location configuration option is set to a location that isn't a valid directory. Please set it to a valid directory and re-execute ssp_stats.")
            sys.exit(0)

        showDaily = self.config.get("stats", "show_daily_requests")

        visualize = self.config.get("stats", "visual_requests")
        visualize_bars = ""

        date_time = time.strftime("%H-%M-%S_%d-%m-%Y")

        # http://www.tutorialspoint.com/python/python_command_line_arguments.htm
        # if sys.argv[1] == "reset":
            # opt = raw_input(":: Are you sure that you want to reset the statistics (y/n)? ")
            # if opt == "y" or opt == "yes":
                # http://stackoverflow.com/a/16649789
                # for key, v in statsDB.iteritems():
                    # del statsDB[key]
                    # print(key)
        # else:
        print(":: Statistics for ssp")
        try:
            option = sys.argv[1]
            if option == "export_csv":
                output = "key, value\n"
                for keys in sorted(statsDB.keys()):
                    output += "%s, %s\n" % (keys, statsDB[keys])
                output_csv = open("%s/ssp_csv_%s.csv" % (self.config.get("stats", "output_csv"), date_time), "w")
                output_csv.write(output)
                output_csv.close()
                print(" :: Statistics exported to %s/ssp_csv_%s.csv" % (self.config.get("stats", "output_csv"), date_time))
            elif option == "export_html":
                keyCount = 0
                for keys in sorted(statsDB.keys()):
                    visualize_bars += "\n                                         [\"%s\", %s]," % (keys, statsDB[keys])
                    keyCount += 1
                # https://developers.google.com/chart/interactive/docs/quick_start#how-about-a-bar-chart
                visualize_html = """
                    <html>
                        <head>
                            <script type="text/javascript" src="https://www.google.com/jsapi"></script>
                            <script type="text/javascript">
                                google.load("visualization", "1.0", {"packages":["corechart"]});
                                google.setOnLoadCallback(drawGraph);
                                function drawGraph() {
                                    var data = new google.visualization.DataTable();
                                    data.addColumn("string", "requests");
                                    data.addColumn("number", "Requests");

                                    data.addRows([
                                        %s
                                    ]);

                                    // http://stackoverflow.com/a/10249847
                                    var options = {
                                        "title": "Number of Requests by Date, Browser and OS",
                                        "width": 1000,
                                        "height": %i,
                                        chartArea: {
                                            top: 50,
                                            left: 400,
                                            width: 1000
                                        }
                                    };

                                    var chart = new google.visualization.BarChart(document.getElementById("chart_div"));
                                    chart.draw(data, options);
                                }
                            </script>
                        </head>
                        <body>
                            <div id="chart_div"></div>
                        </body>
                    </html>
                """ % (visualize_bars[:-1], keyCount*75) # http://stackoverflow.com/a/15478161
                f = open("%s/visualize_html_%s.html" % (self.config.get("stats", "output_html"), date_time), "w")
                f.writelines(visualize_html)
                f.close()
                print(" :: Statistics exported to %s/visualize_html_%s.html" % (self.config.get("stats", "output_html"), date_time))
            else:
                print(" :: Invalid option. Possible options:\n     :: export_csv - Export the keys and values to a csv file.\n     :: export_html - Export the keys and values to a html file.")
        except IndexError:
            try:
                for keys in sorted(statsDB.keys()):
                    if showDaily == "False":
                        if keys[:8] == "requests":
                            pass
                        else:
                            print(" :: %s=%s" % (keys, statsDB[keys]))
                    else:
                        print(" :: %s=%s" % (keys, statsDB[keys]))
            except KeyError:
                print(":: No data.")

if __name__ == "__main__":
    s = ssp_stats()
