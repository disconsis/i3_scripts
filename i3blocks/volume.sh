#!/bin/bash

# picking up last line a amixer output
commandOutput=$(amixer -c 0 get Master | tail -n1);

# extracting volume percentatage
volumeValue=$(echo $commandOutput | cut -d ' ' -f 4 | sed 's/[][]//g');

# extracting mute status
isMute=$(echo $commandOutput | cut -d ' ' -f 6 | sed 's/[][]//g');

if [ "$isMute" = "off" ]
then
    # full name
    echo " $volumeValue";
    
    # short name
    echo " $volumeValue";
    
    # color
    echo "#FF80AB"
else
    # full name
    echo " $volumeValue";
    
    # short name
    echo " $volumeValue";
    
    # color
    echo "#76FF03"
fi