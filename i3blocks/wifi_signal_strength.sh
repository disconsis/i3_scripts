#!/bin/bash

# output for wireless interface
iwconfigOutput=$(iwconfig wlp58s0);

flag=$(iwconfig wlp58s0 | grep "ESSID" | cut -d ':' -f2);

if [ "$flag" = "off/any  " ]; then
    # fullname
    echo " N/A   N/A";
    # shortname
    echo " N/A   N/A";
    # color
    echo "#FF80AB";
else
    # extracting the ssid of the connection
    ssid=$( echo "$iwconfigOutput" | grep "ESSID" | cut -d '"' -f2);
    
    # extracting signal strength of connection
    signalStrength=$( echo "$iwconfigOutput" | grep "Quality" | cut -d '=' -f2 | cut -d ' ' -f1 | bc -l);
    signalStrengthPercentage=$( echo "$signalStrength"*100 | bc | awk '{print int($1)}');
    
    # fullname
    echo " $ssid   $signalStrengthPercentage%";
    # shortname
    echo " $ssid   $signalStrengthPercentage%";
    # color
    echo "#18FFFF";
fi