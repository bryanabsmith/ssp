"""
    ssp authentication credential generator.
"""

import base64
import getpass
import sys


class SSPAuthGen(object):
    """
        Authentication credential generator.
    """

    @staticmethod
    def get_plat():
        """
            Get the platform that the module is being run on.
        """
        return sys.platform

    @staticmethod
    def get_b64():
        """
            Get the base 64 encoded string that contains the username and password.
        """
        name = raw_input(":: Username: ")
        password = getpass.getpass(":: Password: ")
        key = base64.b64encode("%s:%s" % (name, password))
        return str(key)

    def __init__(self):
        print "To generate a key, you will need a username and a password."

        if self.get_plat() == "win32":
            print "\n   Your key is %s. Add this to [auth] > auth_key in ssp.config.\n" % \
                  self.get_b64()
        else:
            print "\n   Your key is \033[0;36;49m%s\033[0m. " \
                  "Add this to [auth] > auth_key in ssp.config.\n" % self.get_b64()


if __name__ == "__main__":
    SSP_AUTH_GEN = SSPAuthGen()
