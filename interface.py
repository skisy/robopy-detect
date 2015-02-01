from Tkinter import *
import objDetect

gui = Tk()

def searchForObject():
    obj = select_li.get(select_li.curselection())
    objDetect.displayMatch(obj)

# Set up label
lbl_txt = StringVar()
search_lbl = Label(gui, textvariable=lbl_txt, relief=RAISED)
lbl_txt.set("Select object to find:")

# Set up list box
select_li = Listbox(gui)
select_li.insert(1, "strep")
select_li.insert(2, "id")
select_li.insert(3, "sid")
select_li.insert(4, "passport")
select_li.insert(5, "IT Card")

# Set up search button
search_btn = Button(gui, text="Search", command=searchForObject)

search_lbl.pack()
select_li.pack()
search_btn.pack()

gui.mainloop()

