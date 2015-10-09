import subprocess
import tarfile

VERSION = "0.1"

print(":: Building ssp...")
subprocess.Popen("pyinstaller ../ssp.py", stdout=subprocess.PIPE, shell=True)

print(":: Building archive...")
# Tar it up
arc = tarfile.open("../ssp_%s.tar" % VERSION, "w")
arc.add("dist/")
arc.close()
