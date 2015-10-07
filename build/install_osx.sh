# This is still a work in progress. This may very well not work.

VERSION=0.1

# http://www.cyberciti.biz/tips/shell-root-user-check-script.html
if [ "$(id -u)" == "0" ]; then
  echo ":: Downloading ssp..."
  curl -O http://www.bryanabsmith.com/ssp/ssp_osx_$VERSION.tar.gz > /dev/null
  echo ":: Unpacking ssp package..."
  tar zxvf ssp_$VERSION.tar.gz > /dev/null
  echo ":: Moving ssp files..."
  mv ssp_$VERSION/* /opt/ssp
  echo ":: Cleaning up..."
  rm -r ssp_$VERSION.tar.gz
  rm -r ssp_$VERSION/
  echo ":: Final steps"
  ln -s /opt/ssp/ssp /usr/bin/ssp
else # http://www.thegeekstuff.com/2010/06/bash-if-statement-examples/
  echo ":: You need to run this script as root."
fi
