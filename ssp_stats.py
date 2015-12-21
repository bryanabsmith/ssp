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
        statsDB = anydbm.open(statsDBLocation, "c")

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
        print(":: Statistics for ssp\n")
        try:
            option = sys.argv[1]
            if option == "export_csv":
                output = "key, value\n"
                for keys in sorted(statsDB.keys()):
                    output += "%s, %s\n" % (keys, statsDB[keys])
                output_csv = open("%s/ssp_csv_%s.csv" % (self.config.get("stats", "output_csv"), date_time), "w")
                output_csv.write(output)
                output_csv.close()
                print(" :: Statistics exported to CSV")
        except IndexError:
            try:
                for keys in sorted(statsDB.keys()):
                    if showDaily == "False":
                        if keys[:8] == "requests":
                            pass
                        else:
                            print(" %s=%s" % (keys, statsDB[keys]))
                    else:
                        print(" %s=%s" % (keys, statsDB[keys]))

                    if visualize == "True":
                        visualize_bars += "\n                                         [\"%s\", %s]," % (keys, statsDB[keys])
                if visualize == "True":
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

                                        var options = {
                                            "title": "Number of Requests by Date, Browser and OS",
                                            "width": 1000,
                                            "height": 2000
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
                    """ % visualize_bars[:-1] # http://stackoverflow.com/a/15478161
                    f = open("visualize_html_%s.html" % date_time, "w")
                    f.writelines(visualize_html)
                    f.close()

            except KeyError:
                print(":: No data.")

if __name__ == "__main__":
    s = ssp_stats()
