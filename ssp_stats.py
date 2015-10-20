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
        print("[Requests]")
        try:
            print(" :: Number of requests (total): %s" % statsDB["requests"])
            print("\n[All Information, Sorted Alphabetically by Key]")
            for keys in sorted(statsDB.keys()):
                print(" :: %s: %s" % (keys, statsDB[keys]))
        except KeyError:
            print(":: No requests received.")

if __name__ == "__main__":
    s = ssp_stats()
