# like-mouseimp
*[MouseImp](https://www.mouseimp.com/)*-like scrolling by dragging the mouse with the right button depressed.<br>
For Linux only.

Features:
- Vertical scroll: <kbd>RBtn</kbd> + Y-drag
- Horizontal scroll: <kbd>LeftShift</kbd> + <kbd>RBtn</kbd> + X-drag


#### NOTES
- Make sure your user is in the correct group (typically `input`) to have read/write access.
- Run `evtest` to determine your mouse and keyboard devices (their corresponding `/dev/input/eventN`), and modify this script accordingly


#### CREDITS
MouseImp is the original great work by Nezhelsky Oskar and Goffmann Svetozar.<br>


#### REF
python-evdev:<br>
https://python-evdev.readthedocs.io/

evtest:<br>
https://man.archlinux.org/man/evtest.1

Add a User to Multiple Linux Groups:<br>
https://www.baeldung.com/linux/add-user-multiple-groups

Input event codes:<br>
https://www.kernel.org/doc/html/latest/input/event-codes.html<br>
https://github.com/torvalds/linux/blob/master/include/uapi/linux/input.h<br>

MouseImp source code (Windows only):<br>
https://www.mouseimp.com/download/<br>
https://github.com/axxie/MouseImp<br>
