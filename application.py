from Tkinter import *
import cv2
import helper as h
import tkFileDialog
import tkMessageBox
import tkFont
import shutil
from os import path as osp
import os
import objDetect
import socket
import py_websockets_bot
import re

def setListboxItems(objects, listbox):
    listbox.delete(0,END)
    for x in range(0, len(objects)):
        listbox.insert(x, objects[x][0])

class MainApp():
    # Initialise GUI
    def __init__(self, master): 

        self.master = master
        self.master.title("DALA")
        self.master.geometry('198x440')

        self.hessian_threshold = 550
        self.min_match = 20
        self.distance = 0.6

        self.search_lbl = Label(self.master, text="Select object to locate")
        self.search_lbl.grid(row=1,column=0,columnspan=2,pady=(8,0))

        self.select_li = Listbox(self.master, width=27,height=15,font=tkFont.Font(family="Helvetica", size=10))

        self.objects = h.processFile('objects.csv')
        setListboxItems(self.objects, self.select_li)

        self.select_li.grid(row=2,column=0, columnspan=2,pady=2,padx=(3,0))

        self.search_btn = Button(self.master, text="Locate", command=self._searchForObject, width=26, height=2)
        self.search_btn.grid(row=3,column=0,columnspan=2,pady=(0,15),padx=(3,0),sticky="ew")

        self.settings_btn = Button(self.master, text="Settings", command=self._openSettings, width=26, height=2)
        self.settings_btn.grid(row=5,column=0,columnspan=2,pady=3,padx=(3,0),sticky="ew")

        self.quit_btn = Button(self.master, text="Quit", command=master.destroy, width=26, height=2)
        self.quit_btn.grid(row=6,column=0,columnspan=2,padx=(3,0),sticky="ew")

    def _openSettings(self):
        settings = Toplevel(self.master)
        set_gui = SettingsDialog(settings,self)

    def _searchForObject(self):
        alg_params = dict([('hes_threshold',self.hessian_threshold),('min_match_num',self.min_match),('good_distance',self.distance)])
        self.master.config(cursor="wait")
        self.master.update()
        #print alg_params['hes_threshold']
        try:
            obj_index = self.select_li.curselection()[0]
            objects = h.processFile('objects.csv')
            objDetect.setupMatch(objects[obj_index][0],objects[obj_index][1],alg_params)
        except IndexError:
            tkMessageBox.showinfo("Oops","Please select an object from the list to locate")
            self.master.config(cursor="")
            self.master.update()
        except socket.error:
            tkMessageBox.showinfo("o Connection","The computer cannot connect to the robot.\nPlease ensure the robot is switched on and\nthe computer is connected to the robot WiFi.")
            self.master.config(cursor="")
            self.master.update()
        self.master.config(cursor="")
        self.master.update()

    def getHessian(self):
        return self.hessian_threshold

    def getMinMatch(self):
        return self.min_match

    def getDistance(self):
        return self.distance

    def getObjects(self):
        return list(self.objects)

    def setHessian(self, value):
        self.hessian_threshold = value

    def setMinMatch(self, value):
        self.min_match = value

    def setDistance(self, value):
        self.distance = value

    def setObjects(self, objects):
        self.objects = objects


class SettingsDialog():

    def __init__(self,master,main):
        self.master = master
        self.master.title("DALA Settings")
        self.master.geometry("700x365")

        master.focus_force()

        self.main = main
        self.objects = main.getObjects()
        #print self.objects

        self.alg_lbl = Label(self.master, text="Algorithm Variables", font=tkFont.Font(family="Helvetica",size=15))
        self.alg_lbl.grid(columnspan=2,row=0,column=0,pady=(5,10),padx=(7,0),sticky=W)

        self.min_match_lbl = Label(self.master, text="Minimum Match Rate:")
        self.min_match_lbl.grid(row=1,column=1,pady=5,sticky=E)

        self.min_match_scale = Scale(self.master, from_=0, to_=50,orient=HORIZONTAL,length=500)
        self.min_match_scale.grid(row=1,column=2,columnspan=3)
        self.min_match_scale.set(main.getMinMatch())

        self.hessian_lbl = Label(self.master, text="Hessian Threshold:")
        self.hessian_lbl.grid(row=2,column=1,pady=5,sticky=E)

        self.hessian_scale = Scale(self.master, from_=0, to_=1000,orient=HORIZONTAL,length=500)
        self.hessian_scale.grid(row=2,column=2,columnspan=3)
        self.hessian_scale.set(main.getHessian())

        self.good_dist_lbl = Label(self.master, text="Good Match Distance:")
        self.good_dist_lbl.grid(row=3,column=1,pady=5,sticky=E)

        self.good_dist_scale = Scale(self.master, from_=0, to_=1,orient=HORIZONTAL,resolution=0.01,length=500)
        self.good_dist_scale.grid(row=3,column=2,columnspan=3)
        self.good_dist_scale.set(main.getDistance())

        self.obj_lbl = Label(self.master, text="Objects",font=tkFont.Font(family="Helvetica",size=15))
        self.obj_lbl.grid(columnspan=2,row=4,column=0,padx=(7,0),pady=(30,10),sticky="w")

        self.add_obj__file_btn = Button(self.master, text="Add Object From File", command=self._openAddObjFile,width=20,height=2)
        self.add_obj__file_btn.grid(row=5, column=1,sticky="w",padx=(5,0))

        self.add_obj_cam_btn = Button(self.master, text="Add Object From Webcam", command=self._openAddObjCam,width=20,height=2)
        self.add_obj_cam_btn.grid(row=5, column=2,sticky="w",padx=(5,0))

        self.add_obj_bot_btn = Button(self.master, text="Add Object From Robot", command=self._openAddObjBot,width=20,height=2)
        self.add_obj_bot_btn.grid(row=5, column=3,sticky="w",padx=(5,0))

        self.remove_obj_btn = Button(self.master, text="Remove Object", command=self._openRemoveObj,width=20,height=2)
        self.remove_obj_btn.grid(row=5,column=4,padx=(5,0), sticky="w")

        self.cancel_btn = Button(self.master, text="Cancel", command=self._close,width=20,height=2)
        self.cancel_btn.grid(row=6, column=0,sticky="w",padx=(5,0),pady=(40,0),columnspan=2)

        self.save_btn = Button(self.master, text="Save", command=self._saveSettings,width=20,height=2)
        self.save_btn.grid(row=6, column=4,sticky="e",pady=(40,0))

    def _close(self):
        self.master.destroy()

    def _saveSettings(self):
        self.main.setHessian(self.hessian_scale.get())
        self.main.setMinMatch(self.min_match_scale.get())
        self.main.setDistance(self.good_dist_scale.get())
        #print self.main.getDistance()
        #print self.main.getMinMatch()
        #print self.main.getHessian()
        self.master.destroy()

    def _openAddObjFile(self):
        add_objects = Toplevel(self.master)
        add_gui = AddObjFileDialog(add_objects,self, self.main)

    def _openAddObjCam(self):
        add_objects = Toplevel(self.master)
        add_gui = AddObjWebcamDialog(add_objects,self, self.main)

    def _openAddObjBot(self):
        add_objects = Toplevel(self.master)
        add_gui = AddObjRobotDialog(add_objects,self, self.main)

    def _openRemoveObj(self):
        remove_objects = Toplevel(self.master)
        rem_gui = RemoveObjDialog(remove_objects,self, self.main)

    def setObjects(self, objects):
        self.objects = objects

    def getObjects(self):
        return list(self.objects)


class ObjFromStreamDialog(object):
    def __init__(self,master,settings,title,main):
        self.master = master;
        self.master.title(title)
        self.master.geometry("405x180") 

        master.focus_force()

        self.settings = settings
        self.main = main

        self.frame = None

        self.obj_lbl = Label(self.master, text="Object Details", font=tkFont.Font(family="Helvetica",size=15))
        self.obj_lbl.grid(columnspan=2,row=0,column=0,pady=(5,10),padx=(7,0),sticky="w")

        self.name_lbl = Label(self.master, text="Object Name:")
        self.name_lbl.grid(row=1,column=0,sticky="e",pady=5)

        self.name = Entry(self.master,width=40)
        self.name.grid(row=1,column=1,sticky="w",columnspan=2)

        self.selected = StringVar()
        self.selected_lbl = Label(self.master, textvariable=self.selected)
        self.selected_lbl.grid(row=2,column=0,sticky="e",pady=(5,0))
        self.selected.set("No Object Selected")

        self.capture_btn = Button(self.master, text="Start Capture",command=self._startCapture, width=20, height=2)
        self.capture_btn.grid(row=2,column=1,columnspan=2,sticky="e",pady=(5,0))

        self.cancel_btn = Button(self.master,text="Cancel",command=self._cancelObjAdd,width=20,height=2)
        self.cancel_btn.grid(row=3,column=0,sticky="w",pady=(10,0),padx=(5,0))

        self.save_btn = Button(self.master,text="Add",command=self._saveObjAdd,width=20,height=2)
        self.save_btn.grid(row=3,column=1,sticky="e",columnspan=2,pady=(10,0))

    def _cancelObjAdd(self):
        self.frame = None
        self.master.destroy()
        self.settings.master.focus_force()

    def _saveObjAdd(self):
        if self.name.get() == "":
            tkMessageBox.showinfo("No Name", "Please give the object a name")
        elif self.frame == None:
            tkMessageBox.showinfo("No Image","Capture and crop object image by clicking 'Start Capture'")
        else:
            name = re.sub("((?=[^s\.])\W)","",self.name.get())
            filename = name + ".jpg"
            filepath = "trainImg/" + filename
            obj = []
            obj.append(name)
            obj.append(filename)
            cv2.imwrite(filepath, self.frame)
            self.settings.objects.append(obj)
            h.writeFile('objects.csv',self.settings.objects)
            self.main.setObjects(list(self.settings.objects))
            setListboxItems(self.main.getObjects(),self.main.select_li)
            self.settings.master.focus_force()
            self.master.destroy()


class AddObjWebcamDialog(ObjFromStreamDialog):
    def __init__(self,master,settings,main):
        ObjFromStreamDialog.__init__(self,master,settings, "Add Object From Webcam", main)

    def _startCapture(self):
        tkMessageBox.showinfo("Control","Select Frame: Spacebar\nCrop: Click top left and bottom right points around object\nQuit: Q")
        selected_frame = None
        frame_selected = False

        cam = cv2.VideoCapture(0)
        while(True):
            ret, img = cam.read()
            cv2.imshow("Object Training", img)
            if cv2.waitKey(1) & 0xFF == 32:
                frame_selected = True
                selected_frame = img
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cam.release()
        cv2.destroyAllWindows()
        if frame_selected:
            self.frame = h.cropImage(selected_frame)
            self.selected.set("Object Selected!")
        self.master.focus_force()

class AddObjRobotDialog(ObjFromStreamDialog):
    def __init__(self,master,settings,main):
        ObjFromStreamDialog.__init__(self,master,settings,"Add Object From Robot")

    def _startCapture(self):
        tkMessageBox.showinfo("Control","Select Frame: Spacebar\nCrop: Click top left and bottom right points around object\nQuit: Q")
        selected_frame = None
        frame_selected = False

        try:
            robot = py_websockets_bot.WebsocketsBot("192.168.42.1")
            robot.start_streaming_camera_images(objDetect.getLastImage)

            while(True):
                try:
                    robot.update()
                    image, image_time = robot.get_latest_camera_image()
                    cv2.imshow( "Image", image )
                    if cv2.waitKey(1) & 0xFF == 32 :
                        frame_selected = True
                        selected_frame = image
                        break
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break 
                except cv2.error:
                    tkMessageBox.showinfo("Feed Error", "Please ensure camera is properly connected and not obstructed")
            robot.disconnect()
            cv2.destroyAllWindows()
            if frame_selected:
                self.frame = h.cropImage(selected_frame)
                self.selected.set("Object Selected!")
            self.master.focus_force()


        except socket.error:
            tkMessageBox.showinfo("No Connection","The computer cannot connect to the robot.\nPlease ensure the robot is switched on and\nthe computer is connected to the robot WiFi.")

class AddObjFileDialog():
    
    def __init__(self,master,settings,main):
        self.master = master;
        self.master.title("Add Object From File")
        self.master.geometry("405x170") 

        master.focus_force()

        self.settings = settings
        self.main = main

        self.filepath = ""
        self.filename = ""

        self.obj_lbl = Label(self.master, text="Ojbect Details", font=tkFont.Font(family="Helvetica",size=15))
        self.obj_lbl.grid(columnspan=2,row=0,column=0,pady=(5,10),padx=(7,0),sticky="w")

        self.name_lbl = Label(self.master, text="Object Name:")
        self.name_lbl.grid(row=1,column=0,sticky="e",pady=5)

        self.name = Entry(self.master,width=40)
        self.name.grid(row=1,column=1,sticky="w",columnspan=2)

        self.path_lbl = Label(self.master, text="Ojbect Image Path:")
        self.path_lbl.grid(row=2,column=0,sticky="e",pady=5,padx=(5,0))

        self.path = Entry(self.master,width=30)
        self.path.grid(row=2,column=1,sticky="w")

        self.path_btn = Button(self.master, text="...",command=self._locateObjImg, width=5)
        self.path_btn.grid(row=2,column=2,sticky="e",padx=(4,0))

        self.cancel_btn = Button(self.master,text="Cancel",command=self._cancelObjAdd,width=20,height=2)
        self.cancel_btn.grid(row=3,column=0,sticky="w",pady=(20,0),padx=(5,0))

        self.save_btn = Button(self.master,text="Add",command=self._saveObjAdd,width=20,height=2)
        self.save_btn.grid(row=3,column=1,sticky="e",columnspan=2,pady=(20,0))

    def _cancelObjAdd(self):
        self.filename = ""
        self.filepath = ""
        self.master.destroy()

    def _saveObjAdd(self):
        if self.filename.endswith(".jpg") or self.filename.endswith(".jpeg") or self.filename.endswith(".png"):
            name = re.sub("((?=[^s\.])\W)","",self.name.get())
            filename = name + ".jpg"
            obj = []
            obj.append(name)
            obj.append(self.filename)
            path, ext = osp.splitext(self.filepath)
            try:
                new_path = "trainImg/" + self.filename
                if not(osp.isfile(new_path)):
                    shutil.copyfile(self.filepath, new_path)
                img = cv2.imread(new_path)
                cropped = h.cropImage(img)
                cv2.imwrite(new_path,cropped)
                self.settings.objects.append(obj)
                h.writeFile('objects.csv',self.settings.objects)
                self.main.setObjects(list(self.settings.objects))
                setListboxItems(self.main.getObjects(),self.main.select_li)
                self.settings.master.focus_force()
                self.master.destroy()
            except shutil.Error:
                tkMessageBox.showinfo("Copy Error","Please check the filepath is valid")
        else:
            tkMessageBox.showinfo("File Type Error","Please select a JPG or PNG")

    def _locateObjImg(self):
        filepath = tkFileDialog.askopenfilename().lower
        if filepath:
            self.path.insert(0,filepath)
            self.filepath = filepath
            path = filepath.split("/")
            self.filename = path[len(path)-1]
            #print self.filepath
            #print self.filename
        self.master.focus_force()


class RemoveObjDialog():
    
    def __init__(self,master,settings,main):
        self.master = master;
        self.master.title("Remove Object")
        self.master.geometry("198x390")

        master.focus_force()

        self.settings = settings
        self.main = main
        self.objects = settings.getObjects()

        self.search_lbl = Label(self.master, text="Select object to remove")
        self.search_lbl.grid(row=0,column=0,pady=(8,0))

        self.remove_li = Listbox(self.master, width=27,height=15,font=tkFont.Font(family="Helvetica", size=10))

        setListboxItems(self.settings.getObjects(),self.remove_li)

        self.remove_li.grid(row=1,column=0,pady=2,padx=(3,0)) 

        self.remove_btn = Button(self.master, text="Remove", command=self._removeObject, width=26, height=2)
        self.remove_btn.grid(row=3,column=0,pady=(0,15),padx=(3,0),sticky="ew")

        self.close_btn = Button(self.master, text="Close",command=self._close,width=26,height=2)
        self.close_btn.grid(row=4,column=0,padx=(3,0),sticky="ew")

    def _removeObject(self):
        try:
            obj_index = self.remove_li.curselection()[0]
            #print self.objects[obj_index]
            self.objects.pop(obj_index)
            setListboxItems(self.objects,self.remove_li)
        except IndexError:
            tkMessageBox.showinfo("Oops","Please select an object from the list to remove")
            self.master.focus_force()

    def _close(self):
        self.settings.setObjects(list(self.objects))
        self.objects = self.settings.getObjects()
        self.main.setObjects(list(self.settings.objects))
        setListboxItems(self.main.getObjects(),self.main.select_li)
        self.master.destroy()

def main():
    root = Tk()
    app = MainApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()