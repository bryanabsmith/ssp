import platform
import urllib
import urllib2

class install_ssp():

    def __init__(self):

        plat = platform.system()
        if plat == "Windows":
            print(":: Downloading ssp for Windows...")
            urllib.urlretrieve("http://www.bryanabsmith.com/ssp/ssp_win_current.zip", "ssp_win_current.zip")
        elif plat == "Darwin":
            self.installMac()
        else:
            print(":: Downloading ssp for Linux...")
            urllib.urlretrieve("http://www.bryanabsmith.com/ssp/ssp_linux_current.tar.gz", "ssp_linux_current.tar.gz")

    def installMac(self):
        print(":: Downloading ssp for OS X...")
        # urllib.urlretrieve("http://www.bryanabsmith.com/ssp/ssp_osx_current.tar.gz", "ssp_osx_current.tar.gz")
        # https://dzone.com/articles/how-download-file-python
        sspFile = urllib2.urlopen("http://www.bryanabsmith.com/ssp/ssp_osx_current.tar.gz")
        sspData = sspFile.read()
        with open("ssp_osx_current.tar.gz", "wb") as ssp:
            ssp.write(sspData)
        


if __name__ == "__main__":
    i = install_ssp()
