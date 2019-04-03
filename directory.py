import os
import tkinter as tk
import tkinter.ttk as ttk
import xml.etree.ElementTree as ET
from tkinter import messagebox


class DirTree(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.tree = ttk.Treeview(self)
        self.tree.config()
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text="Name", anchor='w')
        self.tree["columns"] = ("type")
        self.tree.column("type",width=50)
        self.tree.heading("type", text="Type")
        #abspath = os.path.abspath(path)
        # root_node = self.tree.insert('', 'end', text=abspath, open=True)
        #self.process_directory('', abspath)
        self.tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        self.grid()

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if isdir:
                oid = self.tree.insert(parent, 'end', text=p, open=False)
                self.process_directory(oid, abspath)
            else:
                filename, file_extension = os.path.splitext(p)
                oid = self.tree.insert(parent, 'end', text=filename, open=False, values=(file_extension[1:]))


    def process_xml(self, xml):
        root = ET.fromstring(xml)

        self.tree.delete(*(self.tree).get_children())
        self.process_tree("", root)

    def process_tree(self, parent, root):
        for child in root:
            isdir = True if child.tag == 'dir' else False
            if isdir:
                oid = self.tree.insert(parent, 'end', text=child.attrib['name'])
                self.process_tree(oid, child)
            else:
                file = child.attrib['name']
                filename, file_extension = os.path.splitext(file)
                self.tree.insert(parent, 'end', text=filename, open=False, values=(file_extension[1:]))

    def get_selected_path(self):
        item_id = self.tree.focus()
        try:
             f_type = self.tree.item(item_id)['values'][0]
        except IndexError:
            messagebox.showinfo("Error", "You tried to download a directory")
            return None
        return self.get_selected_rec(item_id) + '.' + f_type

    def get_selected_rec(self, item_id):
        print(self.tree.item(item_id))
        name = self.tree.item(item_id)['text']
        print(name)
        if self.tree.parent(item_id) == "":
            return name
        return os.path.join(self.get_selected_rec(self.tree.parent(item_id)), name)

