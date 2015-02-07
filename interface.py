from Tkinter import *
import objDetect
import tkMessageBox, tkFileDialog
import csv

gui = Tk()

def searchForObject():
    obj = select_li.get(select_li.curselection())
    objDetect.displayMatch(obj)


def processFile():
	with open('objects.csv', 'rb') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		objects = []
		for row in reader:
			objects.append(row)
		return objects

def locateObject():
	obj_file = tkFileDialog.askopenfilename()

	


def addTrainingObject():
	add_obj = Tk()
	
	obj_name_lbl = Label(add_obj, text="Object Name:")

	obj_name = Entry(add_obj)

	path_lbl = Label(add_obj, text="Object Image:")

	filepath = StringVar()
	path = Entry(add_obj, textvariable=filepath)

	loc_obj = Button(add_obj, text="Locate", command=locateObject)

	obj_name_lbl.pack()
	obj_name.pack()
	path_lbl.pack()
	path.pack()
	loc_obj.pack()

# Set up label
search_txt = StringVar()
search_lbl = Label(gui, textvariable=search_txt)
search_txt.set("Select object to find:")

# Set up list box
select_li = Listbox(gui)
objects = processFile()
for x in range(1, len(objects)):
	select_li.insert(x, objects[x][0])

# Set up search button
search_btn = Button(gui, text="Search", command=searchForObject)

# Button to process file
add_btn = Button(gui, text="Add Object", command=addTrainingObject)

search_lbl.pack()
select_li.pack()
search_btn.pack()
add_btn.pack()

gui.mainloop()

