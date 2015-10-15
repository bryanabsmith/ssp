# Tested and works on OS X.

import platform
import shutil
import subprocess

class build_ssp():
    VERSION = "0.1"

    print(":: Building ssp...")
    subprocess.Popen("pyinstaller ../ssp.py > /dev/null", stdout=subprocess.PIPE, shell=True).wait()

    print(":: Building archive...")
    platformName = platform.system()
    if platformName == "Windows":
        shutil.make_archive("ssp_%s" % VERSION, "zip", "dist/")
        print(" :: Archive \"ssp_%s.zip\" created..." % VERSION)
    else:
        shutil.make_archive("ssp_%s" % VERSION, "gztar", "dist/")
        print(" :: Archive \"ssp_%s.tar.gz\" created..." % VERSION)

if __name__ == "__main__":
    b = build_ssp()
