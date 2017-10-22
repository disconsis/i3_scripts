#!/bin/bash

# extracting battery health percentage from acpi output
batteryHealth=$(acpi -ib | rev | cut -d' ' -f 1 | rev | sed -n '2p');

# full name
echo "$batteryHealth";

# short name
echo "$batteryHealth";
