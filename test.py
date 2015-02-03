import Tkinter as tk

class FrameGroup(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.all_instances = []
        self.counter = 0

    def Add(self):
        self.counter += 1
        name = "Frame %s" % self.counter 
        subframe = Subframe(self, name=name)
        subframe.pack(side="left", fill="y")
        self.all_instances.append(subframe)

    def Remove(self, instance):
        # don't allow the user to destroy the last item
        if len(self.all_instances) > 1:
            index = self.all_instances.index(instance)
            subframe = self.all_instances.pop(index)
            subframe.destroy()

    def HowMany(self):
        return len(self.all_instances)

    def ShowMe(self):
        for instance in self.all_instances:
            print(instance.get())

class Subframe(tk.Frame):
    def __init__(self, parent, name):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.e1 = tk.Entry(self)
        self.e2 = tk.Entry(self)
        self.e3 = tk.Entry(self)
        label = tk.Label(self, text=name, anchor="center")
        add_button = tk.Button(self, text="Add", command=self.parent.Add)
        remove_button = tk.Button(self, text="Remove", command=lambda: self.parent.Remove(self))

        label.pack(side="top", fill="x")
        self.e1.pack(side="top", fill="x")
        self.e2.pack(side="top", fill="x")
        self.e3.pack(side="top", fill="x")
        add_button.pack(side="top")
        remove_button.pack(side="top")

    def get(self):
        return (self.e1.get(), self.e2.get(), self.e3.get())

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.master_frame = tk.Frame(self)
        self.master_frame.grid()
        self.all_instances = FrameGroup(self.master_frame)
        self.all_instances.grid()

        # create the first frame
        self.all_instances.Add()

root = GUI()
root.mainloop()