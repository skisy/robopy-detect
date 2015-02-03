from Tkinter import *
import csv
import objDetect

# Add to library class
def processFile(filepath):
	with open('objects.csv', 'rb') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		objects = []
		for row in reader:
			objects.append(row)
		return objects

class DetectAndTrainUI:

	# Initialise GUI
	def __init__(self, master):
		mainFrame = Frame(master)
		mainFrame.pack()

		self.search_lbl = Label(mainFrame, text="Select object to locate")
		self.search_lbl.pack()

		self.select_li = Listbox(mainFrame)
		self.select_li.pack()

		self.objects = processFile('objects.csv')
		self.setObjects(self.objects)

		self.search_btn = Button(mainFrame, text="Locate", command=self.searchForObject)
		self.search_btn.pack()

		self.add_btn = Button(mainFrame, text="Add New Object", command=self.addTrainingObject)
		self.add_btn.pack()

	def searchForObject(self):
		obj_index = self.select_li.curselection()[0]
		objects = processFile('objects.csv')
		objDetect.displayMatch(objects[obj_index][1])

	def addTrainingObject(self):
		print "Add new window?"

	def setObjects(self, objects):
		for x in range(0, len(objects)):
			self.select_li.insert(x, objects[x][0])

root = Tk()
app = DetectAndTrainUI(root)
root.title("Detect And Train")
root.mainloop()



#def locateObject():
#	obj_file = tkFileDialog.askopenfilename()


#def addTrainingObject():
#	add_obj = Tk()
	
#	obj_name_lbl = Label(add_obj, text="Object Name:")

#	obj_name = Entry(add_obj)

#	path_lbl = Label(add_obj, text="Object Image:")

#	filepath = StringVar()
#	path = Entry(add_obj, textvariable=filepath)

#	loc_obj = Button(add_obj, text="Locate", command=locateObject)

	#obj_name_lbl.pack()
	#obj_name.pack()
	#path_lbl.pack()
	#path.pack()
	#loc_obj.pack()