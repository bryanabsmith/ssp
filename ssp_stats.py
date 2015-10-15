# TO DO: reset stats

import anydbm
import ConfigParser

class ssp_stats():

    config = ConfigParser.RawConfigParser(allow_no_value=True)

    def __init__(self):
        self.config.read("ssp.config")

        statsDBLocation = self.config.get("stats", "location")
        statsDB = anydbm.open(statsDBLocation, "c")

        print(":: Statistics for ssp\n")
        print("[Requests]")
        print(" :: Number of requests (total): %s" % statsDB["requests"])
        print("\n[Requests by Date]")
        for keys in statsDB.keys():
            if (keys != "requests"):
                print(" :: %s: %s" % (keys[9:], statsDB[keys]))

if __name__ == "__main__":
    s = ssp_stats()
