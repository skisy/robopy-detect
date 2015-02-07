from Tkinter import *
import tkMessageBox
import tkFont
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

class MainApp():

	# Initialise GUI
	def __init__(self, master):	

		self.hessian = 50
		self.min_match = 20

		self.master = master
		self.master.title("DALA")
		self.master.geometry('198x400')

		self.search_lbl = Label(self.master, text="Select object to locate")
		self.search_lbl.grid(row=1,column=0,columnspan=2,pady=(8,0))

		self.select_li = Listbox(self.master, width=27,height=15,font=tkFont.Font(family="Helvetica", size=10))

		self.objects = processFile('objects.csv')
		self.setObjects(self.objects)

		self.select_li.grid(row=2,column=0, columnspan=2,pady=2,padx=(3,0))

		self.search_btn = Button(self.master, text="Locate", command=self.searchForObject, width=26)
		self.search_btn.grid(row=3,column=0,columnspan=2,pady=(0,15),padx=(3,0),sticky="ew")

		self.settings_btn = Button(self.master, text="Settings", command=self.openSettings, width=26)
		self.settings_btn.grid(row=5,column=0,columnspan=2,pady=3,padx=(3,0),sticky="ew")

		self.quit_btn = Button(self.master, text="Quit", command=master.destroy, width=26)
		self.quit_btn.grid(row=6,column=0,columnspan=2,padx=(3,0),sticky="ew")

	def openSettings(self):
		settings = Toplevel(self.master)
		set_gui = SettingsDialog(settings)

	def searchForObject(self):
		try:
			obj_index = self.select_li.curselection()[0]
			objects = processFile('objects.csv')
			objDetect.displayMatch(objects[obj_index][1])
		except IndexError:
			tkMessageBox.showinfo("Oops","Please select an object from the list")

	def setObjects(self, objects):
		for x in range(0, len(objects)):
			self.select_li.insert(x, objects[x][0])


class SettingsDialog():

	def __init__(self,master):
		self.master = master
		self.master.title("DALA Settings")
		self.master.geometry("600x400")

		self.alg_lbl = Label(self.master, text="Algorithm Variables", font=tkFont.Font(family="Helvetica",size=15))
		self.alg_lbl.grid(columnspan=2,row=0,column=0,pady=(5,10),padx=(7,0))

		self.min_match_lbl = Label(self.master, text="Minimum Match Rate:")
		self.min_match_lbl.grid(row=1,column=1,pady=5)

		self.min_match_scale = Scale(self.master, from_=0, to_=50,orient=HORIZONTAL,length=400)
		self.min_match_scale.grid(row=1,column=2)
		self.min_match_scale.set(20)

		self.hessian_lbl = Label(self.master, text="Hessian Threshold:")
		self.hessian_lbl.grid(row=2,column=1,pady=5)

		self.hessian_scale = Scale(self.master, from_=0, to_=100,orient=HORIZONTAL,length=400)
		self.hessian_scale.grid(row=2,column=2)
		self.hessian_scale.set(50)

		self.good_dist_lbl = Label(self.master, text="Good Match Distance:")
		self.good_dist_lbl.grid(row=3,column=1,pady=5)

		self.good_dist_scle = Scale(self.master, from_=0, to_=1,orient=HORIZONTAL,resolution=0.01,length=400)
		self.good_dist_scle.grid(row=3,column=2)
		self.good_dist_scle.set(0.7)

		self.obj_lbl = Label(self.master, text="Objects",font=tkFont.Font(family="Helvetica",size=15))
		self.obj_lbl.grid(columnspan=2,row=4,column=0,padx=(7,0),pady=(30,10))

class AddObjDialog():
	
	def __init__(self,master):
		self.master = master;
		self.master.title("Add Objects")
		self.master.geometry("300x400") 


class RemoveObjDialog():
	
	def __init__(self,master):
		self.master = master;
		self.master.title("Remove Object")
		self.master.geometry("250x300") 

def main():
	root = Tk()
	app = MainApp(root)
	root.mainloop()

if __name__ == '__main__':
	main()

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