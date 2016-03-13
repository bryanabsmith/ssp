"""
    theatre authentication credential generator.
"""

import base64
import getpass
import sys


class THEATREAuthGen(object):
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
        name = input(":: Username: ")
        password = getpass.getpass(":: Password: ")
        key = base64.b64encode(bytes("{}:{}".format(name, password), "utf-8"))# % (name, password))
        # http://stackoverflow.com/a/606199
        return str(key.decode("utf-8"))

    def __init__(self):
        print("To generate a key, you will need a username and a password.")

        key = self.get_b64()

        if self.get_plat() == "win32":
            print("\n   Your key is {}. Add this to [auth] > auth_key in theatre.config.\n".format(
                  str(key)))
        else:
            print("\n   Your key is \033[0;36;49m{}\033[0m. " \
                  "Add this to [auth] > auth_key in theatre.config.\n".format(str(key)))


if __name__ == "__main__":
    THEATRE_AUTH_GEN = THEATREAuthGen()
