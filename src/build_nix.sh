#!/usr/bin/env bash
clear
echo "\033[0;33;49mBuilding theatre...\033[0m"
pyinstaller -F theatre.py --log-level CRITICAL
echo "\033[0;33;49mBuilding theatre_stats...\033[0m"
pyinstaller -F theatre_stats.py --log-level CRITICAL
echo "\033[0;33;49mBuilding theatre_auth_gen...\033[0m"
pyinstaller -F theatre_auth_gen.py --log-level CRITICAL
echo "\033[0;33;49mCopying appropriate configs and default webroot...\033[0m"
cp ./theatre.config dist/
mkdir dist/webroot/
cp -R webroot/ dist/webroot/
echo "\033[0;33;49mCleaning up build files...\033[0m"
rm -rf build/
mv dist/ theatre_dist/
