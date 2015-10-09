# http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO-5.html
VERSION=0.1

echo ":: Building ssp..."
# http://askubuntu.com/a/98385
cxfreeze ../ssp.py --target-dir ../ssp_$VERSION > /dev/null
echo ":: Copying configuration file..."
cp ../ssp.config ../ssp_$VERSION/ > /dev/null
echo ":: Creating archive..."
# http://www.tecmint.com/18-tar-command-examples-in-linux/
tar -cvjf ../ssp_$VERSION.tar.bz2 ../ssp_$VERSION/ > /dev/null
echo ":: Removing build files..."
rm -rf ../ssp_$VERSION/
