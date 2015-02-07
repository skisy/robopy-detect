from Tkinter import *
from ttk import *
import csv
import objDetect


class Welcome():

	def __init__(self,master):

		self.master=master
		self.master.geometry("250x400")
		self.master.title("Detect and Locate")

		self.label1=Label(self.master,text="Welcome").grid(row=0,column=2)
		self.button1=Button(self.master,text="Open New",command=self.openNew).grid(row=6,column=2)
		self.button2=Button(self.master,text="Quit",command=master.destroy).grid(row=8, column=2)

	def openNew(self):
		root2=Toplevel(self.master)
		myGUI=New(root2)


class New():

	def __init__(self,master):

		self.master=master
		self.master.title("New Window")
		self.label2=Label(self.master,text="New Window").grid(row=0,column=3)

		self.button1=Button(self.master,text="Close",command=master.destroy).grid(row=3,column=3)

def main():
	root=Tk()
	myApp=Welcome(root)
	root.mainloop()

if __name__ == '__main__':
	main()