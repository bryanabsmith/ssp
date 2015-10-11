import ConfigParser
import dbm

class ssp_stats():

    config = ConfigParser.RawConfigParser(allow_no_value=True)

    def __init__(self):
        self.config.read("ssp.config")

        statsDBLocation = self.config.get("stats", "location")
        statsDB = dbm.open(statsDBLocation, "c")

        print(":: Statistics for ssp\n")
        print("[Requests]")
        print(" :: Number of requests (total): %s" % statsDB["requests"])

if __name__ == "__main__":
    s = ssp_stats()
