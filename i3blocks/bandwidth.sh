#!/bin/bash

# reading arguments
# if [[ $# -ge 4 ]]; then
#     uploadIcon=$1;
#     downloadIcon=$2;
#     uploadColor=$3;
#     downloadColor=$4;
#     elif [[ $# -eq 2 ]]; then
#     iface=$1;
#     ssidColor=$2;
#     signalColor=$3;
#     offColor=$4;
#     elif [[ $# -eq 3 ]]; then
#     iface=$1;
#     ssidColor=$2;
#     signalColor=$3;
#     elif [[ $# -eq 2 ]]; then
#     iface=$1;
#     ssidColor=$2;
#     elif [[ $# -eq 1 ]]; then
#     iface=$1;
# else
#     echo "iface needed. ERROR!!"
#     exit;
# fi

# /proc/net/dev output for wlp58s0 interface
networkInformation=$(cat /proc/net/dev | grep wlp58s0);

# received bytes at time T
receivedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $2}');

# Transmitted bytes at time T
transmittedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $10}');

# pause for 1 second
sleep 1s

# received bytes at time T + 1
newReceivedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $2}');

# Transmitted bytes at times T + 1
newTransmittedBytes=$(cat /proc/net/dev | grep wlp58s0 | awk -v N=2 '{print $10}');

# Convertion to KiloBytes
receivedKBs=$(echo "($newReceivedBytes-$receivedBytes)/1024" | bc -l | awk '{print int($1)}');

# Convertion to KiloBytes
transmittedKBs=$(echo "($newTransmittedBytes-$transmittedBytes)/1024" | bc -l | awk '{print int($1)}');

# fullname
echo " $transmittedKBs KB/s   $receivedKBs KB/s";

# shortname
echo " $transmittedKBs KB/s   $receivedKBs KB/s";