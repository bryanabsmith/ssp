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
                date_time = time.strftime("%H-%M-%S_%d-%m-%Y")
                for keys in sorted(statsDB.keys()):
                    output += "%s, %s\n" % (keys, statsDB[keys])
                output_csv = open("%s/ssp_csv_%s.csv" % (self.config.get("stats", "output_csv"), date_time), "w")
                output_csv.write(output)
                output_csv.close()
                print(" :: Statistics exported to CSV")
        except IndexError:
            try:
                for keys in sorted(statsDB.keys()):
                    #print(" :: %s: %s" % (keys, statsDB[keys]))
                    print(" %s=%s" % (keys, statsDB[keys]))
            except KeyError:
                print(":: No data.")

if __name__ == "__main__":
    s = ssp_stats()
