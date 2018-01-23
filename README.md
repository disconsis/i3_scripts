# Scripts for myriad i3 functionality

## i3

### focus-last.py
---

#### Description
Changes to the last focused window on `Alt-Tab` (or whatever you change it to)  
Borrowed heavily from [acrisici/i3ipc-python/examples/focus-last.py](https://github.com/acrisci/i3ipc-python/focus-last.py)

#### Usage
Run it first as a daemon to begin window history logging  
`python3 focus-last.py &!`  
Switch to the last focused window with  
`python3 focus-last.py --switch`  

#### Configuration
There's only one configuration parameter, really - the maximum window history length  
Typically, we only care about the second window in this list, since that's the last focused window. However, in case this window was closed in some way other than moving to it and closing it, the 3rd window in the list would be the last focused window, and so on.
This can be set in **settings.yaml** -
```yaml
window history length: <num>
```

### find\_apps.py
---

#### Description
Changes workspace names to add glyphs of all the contained windows  
Workspace names with glyphs look like - `<num>: <glyphs>`
Glyphs can be configured for each application class  
Applications supported right now are:  

1. download manager
    - uget
2. browser
    - Firefox
    - Google Chrome
    - qutebrowser
3. youtube
    - if using one of the above browsers
4. ebook reader
    - Okular
    - Zathura
5. virtual machine
    - VirtualBox
    - VMware player
6. media player
    - vlc/cvlc
7. wireshark
8. terminal
    - Gnome terminal
    - URxvt
    - XTerm
    - st (suckless terminal)
9. file browser
    - Nautilus
10. image viewer
    - Pinta
    - pqiv
    - feh
    - Eog
11. fontforge
12. office
    - libre office
13. Gvim
14. editor
    - Gedit
15. Spim (MIPS simulator)

Adding new applications / classes is also pretty easy - see Configuration  
  
The currently focused application is highlighted in a user-defined colour.  
If used along with **focus-last.py**, the last focused application is also highlighted (in a different colour). This helps as a visual indicator of which window you'll jump back to if you hit your keybind for `focus-last.py --switch`.

#### Usage
Simply run it as a daemon:
```sh
python3 find_apps.py &!
```

#### Configuration
Glyphs for application classes can be configured by altering the **settings.yaml** file.  
They are set in the format -
```yaml
glyphs:
    app class name: glyph
    ...
```
The default glyphs are [nerd font](https://github.com/ryanoasis/nerd-fonts) icons, so they might look weird if you're using a different font.
  
Colors for the currently and last focused can also be altered in the same way -
```yaml
colors:
    focused: <color>
    last focused: <color>
```
\<color\> can be specified according to [X11 color names](https://wikipedia.org/wiki/X11_color_names#Color_name_chart), or an RGB color specification (#RRGGBB).  
RGB color codes need to be wrapped in quotes since # starts a comment in yaml.  
Since i3 v4.12, i3bar also supports transparency, so an RGBA color codes can also be used.  

Adding support for new applications is simple -  
1. Open the application
2. Open a terminal and run `python3 find\_apps.py debug` to list current windows to find the details of your window
3. Add/update an `elif` clause in the function get\_app() (use the others defined as a guide)
4. If you're adding a new application class, add an entry in **settings.yaml** and return the glyph from the function

If that looks complicated, or you need something more complex, just open an issue :stuck\_out\_tongue\_winking\_eye:

If you change any settings, you'll want to restart the daemons. If you change things often, this soon becomes a pain. Put this in your i3 config to make this easy -
```conf
exec_always --no-startup-id python3 <path_to_repo>/i3/find_apps.py
exec_always --no-startup-id python3 <path_to_repo>/i3/focus-last.py
bindsym $mod+Shift+z exec "pkill -f <path_to_repo>/i3/";restart
```
Hitting $mod+Shift+z now restarts i3 as well as the scripts

### rename\_ws.py
---

#### Description
Only useful with **find\_apps.py**  
Assigns/removes custom names to workspaces _while_ keeping all the glyphs from find_apps.py  
Workspaces with custom names look like `<num>: <custom name>: <glyphs>`  
  
Another feature is the ability to re-number workspaces on the basis of your monitor setup.  
Outputs (monitors) are sorted on the basis of their position - first on y, then on x.
Workspaces are incrementally numbered on the basis of the output they belong in and their position within that output.  

For example,  
```
  Output 1      Output 2                Output 1       Output 2
+-----------+ +-----------+           +-----------+ +-----------+  
|           | |           |           |           | |           |  
|___________| |___________|   --->    |___________| |___________|  
|4|6|7|9|   | |1|2|3|5|8| |           |1|2|3|4|   | |5|6|7|8|9| |  
+-----------+ +-----------+           +-----------+ +-----------+  
```
(workspaces are renumbered, not moved around)

#### Usage
To rename the current workspace
```sh
python3 rename_ws.py rename <custom_name>
```
Since it's not feasible to run this command inside any window manually, this is best rebinded so that it can take input externally and run it.  
i3-input is great for such tasks, although it leaves something to be desired when it comes to looks.  
```
bindsym $mod+n exec i3-input -F 'exec python3 <path_to_repo>/i3/rename_ws.py rename "%s"'
```
Hitting $mod+n now pops up a textbox in which the custom name can be entered.  
  
To remove a custom name, you have two options -
1. Rename with an empty name - hit your keybind for `rename` and press enter, or `python3 rename_ws.py rename ''`
2. Use the `remove` command - `python3 rename_ws.py remove`

Using an empty rename has the benefit that it saves a keybind  
Using the remove command has the benefit that it saves the textbox popping up  

To reorder the workspaces,
```sh
python3 rename_ws.py reorder
```

### mouse.py
---
#### Description
Enable, disable or toggle the state of all pointing devices collectively  
The mouse pointer is moved to the right bottom corner before disabling.
Also creates a temp file to indicate that pointing devices are enabled (used by **i3blocks/check\_mouse**)
#### Usage
Fairly intuitive commands -
```sh
python3 mouse.py enable
python3 mouse.py disable
python3 mouse.py toggle
```
If you're using this with **i3blocks/check_mouse**, it is neccessary to signal i3blocks to update the block.
```conf
bindsym $mod+grave exec "python ~/.config/i3blocks/scripts/mouse toggle; pkill -RTMIN+2 i3blocks"
```

### Dependencies
---
The scripts depend on:
1. i3ipc
2. fasteners
3. selectors
4. python3-xlib
5. pyautogui
6. pyyaml

Install dependencies by running
```sh
cd <path_to_repo>
pip3 install -r i3/requirements.txt
```

## i3blocks
*Note: Arguments in square brackets are mandatory while italicized ones are optional*

- **check\_capslock**  
	- **Markup:** none
	- **Description:** Checks the current status of capslock

- **check\_mouse**  
	- **Markup:** none
	- **Description:** Checks the current status of pointing devices. Checks the flag set by **i3/mouse.py** to detect the state of pointing devices.

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
