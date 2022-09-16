import tkinter as tk
import serial
import time
from threading import Timer

printer_sport = "/dev/tty.usbserial-2110"
printer_port = serial.Serial(printer_sport, 115200, timeout=1)

relay_loc = "/dev/tty.usbserial-2120"
relay_port = serial.Serial(relay_loc, 9600)


REST_HEIGHT = 1000
HOME_LOC_X = 85
HOME_LOC_Y = 165
HOME_LOC_Z = 80
DEFAULT_PUMP_TIME="1"
CUP_SPACING=53

def pump_on():
    relay_port.write(bytes.fromhex("A0 01 01 A2"))

def pump_off():
    relay_port.write(bytes.fromhex("A0 01 00 A1"))

def send_cmd(cmd):
    print(cmd)
    printer_port.write(f"{cmd}\n".encode("ASCII"))

def autohome():
    send_cmd("G28")

def move(x=None, y=None, z=None):
    s = "G0"
    if x is not None:
        s += f"X{x}"
    if y is not None:
        s += f"Y{y}"
    if z is not None:
        s += f"Z{z}"
    
    s+= "F5000"
    send_cmd(s)


def move_relative(x=None, y=None, z=None):
    send_cmd("G91")
    move(x,y,z)

def move_absolute(x=None, y=None, z=None):
    send_cmd("G90")
    move(x,y,z)

def up_ten():
    move_relative(z=10)

def down_ten():
    move_relative(z=-10)

def go_home():
    move_absolute(x=HOME_LOC_X, y=HOME_LOC_Y, z=HOME_LOC_Z)

def shots():
    # get input values
    go_home()
    pour_time = float(inputtxt.get())
    num_shots = int(num_shots_entry.get())
    if num_shots > 9:
        return
    
    row_x = 0
    row_y = 0

    pos_order = [
        [0,0],
        [1,0],
        [2,0],
        [2,1],
        [1,1],
        [0,1],
        [0,2],
        [1,2],
        [2,2],
    ]
    effective_pos_order = pos_order[0:num_shots]
    abs_mm_cords = []
    for cup_cord in effective_pos_order:
        cord = []
        cord.append(HOME_LOC_X + (cup_cord[0] * CUP_SPACING))
        cord.append(HOME_LOC_Y - (cup_cord[1] * CUP_SPACING))
        abs_mm_cords.append(cord)

    #main control loop
    if num_shots == 1:
        pump_on()
        time.sleep(pour_time)
        pump_off()
        return

    CENTER_TO_EDGE_TIME = 0.2
    EDGE_TO_EDGE_TIME = 0.5
    for i, abs_cord in enumerate(abs_mm_cords):
        is_first = i == 0
        is_last = i == len(abs_mm_cords) - 1
        if is_first:
            pump_on()
            time.sleep(pour_time - CENTER_TO_EDGE_TIME)
        elif not is_last:
            move_absolute(x=abs_cord[0], y=abs_cord[1])
            time.sleep(CENTER_TO_EDGE_TIME)
            pump_off()
            time.sleep(EDGE_TO_EDGE_TIME)
            pump_on()
            time.sleep(pour_time - CENTER_TO_EDGE_TIME * 2)
        else:
            move_absolute(x=abs_cord[0], y=abs_cord[1])
            time.sleep(CENTER_TO_EDGE_TIME)
            pump_off()
            time.sleep(EDGE_TO_EDGE_TIME)
            pump_on()
            time.sleep(pour_time)
            pump_off()

    go_home()




root = tk.Tk()
root.title("ShotBot V0.420.69")

button = tk.Button(root, text="+10MM Z", command=up_ten)
button.pack()

button = tk.Button(root, text="-10MM Z", command=down_ten)
button.pack()

button = tk.Button(root, text="Force Pump On", command=pump_on)
button.pack()

button = tk.Button(root, text="Force Pump Off", command=pump_off)
button.pack()

button = tk.Button(root, text="home", command=go_home)
button.pack()

label = tk.Label(root, text="Pumptime per shot")
label.pack()

inputtxt = tk.Entry(root)
inputtxt.insert(0, DEFAULT_PUMP_TIME)
inputtxt.pack()

num_shots_label = tk.Label(root, text="# of shots")
num_shots_label.pack()

num_shots_entry = tk.Entry(root)
num_shots_entry.insert(0, 9)
num_shots_entry.pack()

shot_button= tk.Button(root, text="SHOTS", font='Script 20', command=shots)
shot_button.pack()

root.mainloop()

