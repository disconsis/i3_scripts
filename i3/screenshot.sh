#!/bin/bash

# creating files name using current date time
fileName=$(date +"%Y_%m_%d_%H_%M_%S" );

# using imagemagik to capture the whole X server root and save it
import -window root ~/Pictures/Screenshots/$fileName.jpg