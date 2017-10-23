# Scripts for myriad i3 functionality

## i3

- **find\_apps.py**  
	- **Description:** Changes workspace names to add glyphs of all the contained windows  
Highlights the currently focused and the last focused window in the bar

- **focus-last.py**  
	- **Description:** Changes to the last focused app on `Alt-Tab` (or whatever you change it to)

- **mouse.py**  
	- **Description:** Enables or disables all pointing devices 

- **rename\_ws.py**  
	- **Description:** Changes workspace names while keeping all the glyphs from **find\_apps.py**

## i3blocks
*Note: Arguments in square brackets are mandatory while italicized ones are optional*

- **check\_capslock**  
	- **Markup:** none
	- **Description:** Checks the current status of capslock

- **check\_mouse**  
	- **Markup:** none
	- **Description:** Checks the current status of pointing devices

- **disk\_acc**  
	- **Markup:** none
	- **Description:** Accurate depiction of free disk space

- **wifi\_signal\_strength**
	- **Arguments:** [interface] *ssidColor* *signalColor* *offColor* *separatorColor*  
	- **Example:** wifi_signal_strength.sh wlp58s0 "#ff80ab" "#69F0AE" "#ff80ab" "#8b96d2"
	- **Markup:** pango
	- **Description:** Shows the wifi SSID and singal strength of the mentioned interface. Shows N/A incase no connection is found.

- **battery\_health** 
	- **Markup:** none
	- **Description:** Shows the battery health ( A new laptop should show something around 98% )

- **battery**  
	- **Description:** Shows the battery life, with dynamic icons for different levels. Icons are also provided to represent consumption and charging.

- **screenshot**  
	- **Markup:** none
	- **Description:** Takes a screen shot of the whole screen and saves it in the ~/Pictures/Screenshots/ directory with the filename of current date & time.

- **bandwidth**  
	- **Description:** Tells the correct network traffic in KB/s from /proc/net/dev file.

- **date**  
	- **Markup:** none
	- **Description:** Tells the date in the format of <Week Day, day of month, month name, year>.

- **time**  
	- **Markup:** none
	- **Description:** Tells the current time in the format of <Hour, Minute, AM/PM>
