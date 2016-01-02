# This is still a work in progress. This may very well not work.
# By default, Windows doesn't let you run unsigned PowerShell scripts. To execute this, run the following first:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
# After doing this, change the policy back to the default:
#

$version="0.1"
$dl_source="http://www.bryanabsmith.com/ssp/ssp_win_$version.zip"

write-output ":: Downloading ssp..."
write-output ":: Getting $dl_source"

# http://www.powershellatoms.com/basic/download-file-website-powershell/
