# http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO-5.html
VERSION=0.1

echo ":: Building ssp..."
# http://askubuntu.com/a/98385
cxfreeze ../ssp.py --target-dir ../ssp_$VERSION > /dev/null
echo ":: Copying configuration file..."
cp ../ssp.config ../ssp_$VERSION/ > /dev/null
