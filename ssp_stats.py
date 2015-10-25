# TO DO: reset stats

import anydbm
import ConfigParser
import sys

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
            print(sys.argv[1])
        except IndexError:
            try:
                for keys in sorted(statsDB.keys()):
                    #print(" :: %s: %s" % (keys, statsDB[keys]))
                    print(" %s=%s" % (keys, statsDB[keys]))
            except KeyError:
                print(":: No data.")

if __name__ == "__main__":
    s = ssp_stats()
