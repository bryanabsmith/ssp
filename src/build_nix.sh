#!/usr/bin/env bash
clear
echo "\033[0;33;49mBuilding ssp...\033[0m"
pyinstaller -F ssp.py --log-level CRITICAL
echo "\033[0;33;49mBuilding ssp_stats...\033[0m"
pyinstaller -F ssp_stats.py --log-level CRITICAL
echo "\033[0;33;49mBuilding ssp_auth_gen...\033[0m"
pyinstaller -F ssp_auth_gen.py --log-level CRITICAL
echo "\033[0;33;49mCopying appropriate configs and default webroot...\033[0m"
cp ./ssp.config dist/
mkdir dist/webroot/
cp -R webroot/ dist/webroot/
echo "\033[0;33;49mCleaning up build files...\033[0m"
rm -rf build/
mv dist/ ssp_dist/
mv ssp_dist/dist/ssp ssp_dist/