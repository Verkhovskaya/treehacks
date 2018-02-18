import time
import serial
import sys
sys.path.append("/Users/2017-A/Dropbox/python_libraries/PyCAD")
from figure import Figure
fig = Figure()
ser = serial.Serial('/dev/cu.usbmodem1411')  # open serial port

def getData():
	ser.flushInput()
	while True:
		if "###" in str(ser.readline()):
			break
	data = [ser.readline().strip() for i in range(6)]
	for each in data:
		if '#' in str(each):
			return getData()
	return [int(i) for i in data]


def testGetData():
	for i in range(5):
		print(getData())
		time.sleep(1)


if len(sys.argv) == 2:
	testGetData()
elif len(sys.argv) == 3:
	while True:
		testGetData()

zero = getData()


def normalize(data):
	return [max(1, (data[i]-zero[i])*1024/(1024-max(*zero))) for i in range(6)]


from vpython import *
scene.width = 1420
scene.height = 765
scene.autoscale = False
scene.range = 20
scene.fov = 0.5
scene.userspin = True

draw_color = (1,1,1)

def new_red(new_val):
	global draw_color
	draw_color = (draw_color[0], draw_color[0], draw_color[2])

def new_green(new_val):
	global draw_color
	draw_color = (draw_color[0], (new_val/255.0), draw_color[2])

def new_blue(new_val):
	global draw_color
	draw_color = (draw_color[0], draw_color[1], (new_val/255.0))

colors = {"Black":(0,0,0), "Grey":(0.4, 0.4, 0.4), "White":(1,1,1), "Magenta":(148.0/255, 0, 211.0/255), "Purple":(75.0/255, 0, 130), "Blue":(0,0,1), "Cyan": (0,1,1), "Green":(0,1,0), "Yellow":(1,1,0), "Orange":(1,0.5,0), "Red":(1,0,0)}

text_colors = {"Black":color.white, "Grey":color.white, "Magenta":color.white, "Purple":color.white, "Blue":color.white, "Cyan": color.black, "Green":color.black, "Yellow":color.black, "Orange":color.black, "Red":color.black, "White":color.black}


current_color = vector(1,1,1)

# Lambdas are causing bugs and it's too late to think.
def toblack():
	global current_color
	current_color = vector(0,0,0)
def togrey():
	global current_color
	current_color = vector(0.4, 0.4, 0.4)
def towhite():
	global current_color
	current_color = vector(1,1,1)
def tomagenta():
	global current_color
	current_color = vector(148.0/255, 0, 211.0/255)
def topurple():
	global current_color
	current_color = vector(75.0/255, 0, 130)
def toblue():
	global current_color
	current_color = vector(0,0,1)
def tocyan():
	global current_color
	current_color = vector(0,1,1)
def togreen():
	global current_color
	current_color = vector(0,1,0)
def toyellow():
	global current_color
	current_color = vector(1,1,0)
def toorange():
	global current_color
	current_color = vector(1,0.5,0)
def tored():
	global current_color
	current_color = vector(1,0,0)
color_funcs = {"Black":toblack, "Grey":togrey, "White":towhite, "Magenta":tomagenta, "Purple":topurple, "Blue":toblue, "Cyan":tocyan, "Green":togreen, "Yellow":toyellow, "Orange":toorange, "Red":tored}


def make_stl():
	global fig
	fig.generate_stl()

layout = [(0, -1), (-0.7, 0.5), (0.7, 0.5), (-0.7, -0.5), (0, 0), (0.7, -0.5)]
def getPosition(data):
	top_positions = [None, None, None]
	top_readings = [0,0,0]
	data = normalize(data)
	for each in data:
		if each > top_readings[0]:
			top_positions = [layout[data.index(each)]] + top_positions[:2]
			top_readings = [each] + top_readings[:2]
		elif each > top_readings[1]:
			top_positions = [top_positions[0]] + [layout[data.index(each)]] + [top_positions[1]]
			top_readings = [top_readings[0]] + [each] + [top_readings[1]]
		elif each > top_readings[2]:
			top_positions = top_positions[:2] + [layout[data.index(each)]]
			top_readings = top_readings[:2] + [each]
	x = 40*sum([top_positions[x][0]*top_readings[x]/sum(top_readings[:3]) for x in range(3)])
	y = 10-(top_readings[0]+top_readings[1])/50
	z = -20-40*sum([top_positions[x][1]*top_readings[x]/sum(top_readings[:3]) for x in range(3)])
	return x,y,z

scene.append_to_caption("\n  ")
for each in colors:
	button(text=each, bind=color_funcs[each], background=vector(*colors[each]), textcolor = text_colors[each])
	scene.append_to_caption("   ")

scene.append_to_caption(" "*8)
button(text=" "*16 + "Generate STL" + " "*16, bind=make_stl)


wtext(text= " "*8)
wtext(text= " X: ")
x_pos_text = wtext(text="00000")
wtext(text= "  Y: ")
y_pos_text = wtext(text="00000")
wtext(text= "  Z: ")
z_pos_text = wtext(text="00000")

last = getPosition(getData())
pointer = sphere(pos=vector(*last), radius=1.2, color=vector(1,0,0))

current_cylinder = cylinder(pos=vector(*last), axis=vector(0,0,0), radius=1, color=current_color)
current_cylinder.visible = False
data = getData()

def keyInput(evt):
    global current_cylinder
    global last
    s = evt.key
    if s == " ":
        last = getPosition(data)
        if current_cylinder.visible:
            start_point = current_cylinder.pos
            fig.line((start_point.x, start_point.y, start_point.z), last)
        current_cylinder = cylinder(color=current_color, pos=vector(*last), axis=vector(0,0,0), radius=1)
    elif s == "esc":
        current_cylinder.visible = False

scene.bind('keydown', keyInput)

while True:
	data = getData()
	next_location = getPosition(getData())
	new_x_text = str(int(next_location[0]))
	x_pos_text.text = " "*(5-len(new_x_text)) + new_x_text
	new_y_text = str(int(next_location[1]))
	y_pos_text.text = " "*(5-len(new_y_text)) + new_y_text
	new_z_text = str(int(next_location[2]))
	z_pos_text.text = " "*(5-len(new_z_text)) + new_z_text
	pointer.pos = vector(*next_location)
	current_cylinder.axis = vector(next_location[0]-last[0], next_location[1]-last[1], next_location[2]-last[2])
	current_cylinder.color = current_color

sphere(pos=vector(*last), radius=radius)
print(last)
for i in range(10):
	next = getPosition()
	print(next)
	sphere(pos=vector(*next))

ser.close()