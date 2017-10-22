#!/bin/bash

# default variable values
offColor="#ffffff";
ssidColor="#ffffff";
signalColor="#ffffff";
innerSeparatorColor="#ffffff";

# output for wireless interface ( if ssidc sigc offc insc )
if [[ $# -ge 5 ]]; then
    iface=$1;
    ssidColor=$2;
    signalColor=$3;
    offColor=$4;
    innerSeparatorColor=$5;
elif [[ $# -eq 4 ]]; then
    iface=$1;
    ssidColor=$2;
    signalColor=$3;
    offColor=$4;
elif [[ $# -eq 3 ]]; then
    iface=$1;
    ssidColor=$2;
    signalColor=$3;
elif [[ $# -eq 2 ]]; then
    iface=$1;
    ssidColor=$2;
elif [[ $# -eq 1 ]]; then
    iface=$1;
else
    echo "iface needed. ERROR!!"
    exit;
fi

iwconfigOutput=$(iwconfig $iface);

flag=$(echo $iwconfigOutput | grep "ESSID" | cut -d ':' -f2);

if [ "$flag" = "off/any  " ]; then
    # fullname
    echo "<span foreground='$offColor'> N/A</span> <span foreground='$innerSeparatorColor'> ∙ </span> <span foreground='$offColor'> N/A</span>";
    # shortname
    echo "<span foreground='$offColor'> N/A</span> <span foreground='$innerSeparatorColor'> ∙ </span> <span foreground='$offColor'> N/A</span>";
else
    # extracting the ssid of the connection
    ssid=$( echo "$iwconfigOutput" | grep "ESSID" | cut -d '"' -f2);
    
    # extracting signal strength of connection
    signalStrength=$( echo "$iwconfigOutput" | grep "Quality" | cut -d '=' -f2 | cut -d ' ' -f1 | bc -l);
    signalStrengthPercentage=$( echo "$signalStrength"*100 | bc | awk '{print int($1)}');
    
    # fullname
    echo "<span foreground='$ssidColor'> $ssid</span> <span foreground='$innerSeparatorColor'> ∙ </span> <span foreground='$signalColor'> $signalStrengthPercentage%</span>";
    # shortname
    echo "<span foreground='$ssidColor'> $ssid</span> <span foreground='$innerSeparatorColor'> ∙ </span> <span foreground='$signalColor'> $signalStrengthPercentage%</span>";
fi
