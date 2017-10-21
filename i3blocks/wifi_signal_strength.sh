#!/bin/bash

# output for wireless interface
if [[ $# -ge 1 ]]; then
    iface=$1
else
    iface="wlp58s0"
fi

iwconfigOutput=$(iwconfig $iface);

flag=$(echo $iwconfigOutput | grep "ESSID" | cut -d ':' -f2);

if [ "$flag" = "off/any  " ]; then
    # fullname
    echo " N/A   N/A";
    # shortname
    echo " N/A   N/A";
    # color
    echo "#FF8A80";
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
    echo "#A7FFEB";
fi
