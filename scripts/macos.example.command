#!/bin/bash

CERTIFICATE_NAME='<certificate name here>'
ABLETON_APP_NAME='Ableton Live 12 Suite.app'

###################################################################################################
# DO NOT MODIFY THESE COMMANDS UNLESS YOU KNOW WHAT YOU'RE DOING.
###################################################################################################

sudo xattr -d -r com.apple.quarantine "/Applications/${ABLETON_APP_NAME}"
sudo codesign --force --sign ${CERTIFICATE_NAME} "/Applications/${ABLETON_APP_NAME}"
