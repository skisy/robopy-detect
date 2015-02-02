from Tkinter import *
import objDetect
import tkMessageBox
import csv

gui = Tk()

def searchForObject():
    obj = select_li.get(select_li.curselection())
    objDetect.displayMatch(obj)


def processFile():
	with open('objects.csv', 'rb') as csv_file:
		reader = csv.reader(csv_file, delimiter=' ')
		for row in reader:
			print row

# Set up label
lbl_txt = StringVar()
search_lbl = Label(gui, textvariable=lbl_txt, relief=RAISED)
lbl_txt.set("Select object to find:")

# Set up list box
select_li = Listbox(gui)
select_li.insert(1, "strep")
select_li.insert(2, "staff")
select_li.insert(3, "student")
select_li.insert(4, "passport")
select_li.insert(5, "card")

# Set up search button
search_btn = Button(gui, text="Search", command=searchForObject)

# Button to process file
process_btn = Button(gui, text="Process File", command=processFile)

search_lbl.pack()
select_li.pack()
search_btn.pack()
process_btn.pack()

gui.mainloop()

