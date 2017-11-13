#!/bin/bash

# Keep master at 60% for speaker and 25% for earphone profile for best results

# picking up last line a amixer PCM channel
commandOutput=$(amixer -M -c 0 get PCM | tail -n1);

# pick up values for mute status from Master channel
muteValue=$(amixer -M -c 0 get Master | tail -n1);

# extracting volume percentatage
volumeValue=$(echo $commandOutput | cut -d ' ' -f 5 | sed 's/[][]//g');

# extracting mute status
isMute=$(echo $muteValue | cut -d ' ' -f 6 | sed 's/[][]//g');

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