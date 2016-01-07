#/bin/bash

# http://stackoverflow.com/a/21372328
if [[ $(id -u) -ne 0 ]]; then
  echo "Please execute the installer as root (or use sudo)"
else
  echo ":: Making ssp directory in /opt/"
  mkdir -p /opt/ssp/
  echo ":: Copying contents to /opt/ssp/"
  cp -R * /opt/ssp/
  echo ":: Creating symlinks"
  ln -s /opt/ssp/src/ssp.py /usr/bin/ssp
  ln -s /opt/ssp/src/ssp_stats.py /usr/bin/ssp_stats
  echo ":: Fixing permissions"
  chmod +x /opt/ssp/src/ssp.py
  chmod +x /opt/ssp/src/ssp_stats.py
  echo "Done"
fi
