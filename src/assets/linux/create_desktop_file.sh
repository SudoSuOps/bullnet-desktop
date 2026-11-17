#!/bin/sh
set -e

WORKING_DIR=$(pwd)
THIS_PATH=$(readlink -f "$0")
cd "$(dirname "$THIS_PATH")"
FULL_PATH=$(pwd)
cd "$WORKING_DIR"

cat <<EOS > ai.bullnet.Desktop.desktop
[Desktop Entry]
Name=BullNet
Comment=BullNet - your private AI office
Exec="${FULL_PATH}/ai.bullnet.Desktop" %U
Terminal=false
Type=Application
MimeType=x-scheme-handler/mattermost
Icon="${FULL_PATH}/app_icon.png"
Categories=Network;InstantMessaging;
StartupWMClass=ai.bullnet.Desktop
EOS

chmod +x ai.bullnet.Desktop.desktop
