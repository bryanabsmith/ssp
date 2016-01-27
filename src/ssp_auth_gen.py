import base64
import getpass
import sys

class ssp_auth_gen():

    def __init__(self):
        PLAT = sys.platform

        print("To generate a key, you will need a username and a password.")
        name = raw_input(":: Username: ")
        password = getpass.getpass(":: Password: ")
        key = base64.b64encode("%s:%s" % (name, password))

        if PLAT == "win32":
            print("\n   Your key is %s. Add this to [auth] > auth_key in ssp.config.\n" % key)
        else:
            print("\n   Your key is \033[0;36;49m%s\033[0m. Add this to [auth] > auth_key in ssp.config.\n" % key)

if __name__ == "__main__":
    s = ssp_auth_gen()