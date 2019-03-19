import os
import tkinter as tk
import tkinter.ttk as ttk


class DirTree(tk.Frame):
    def __init__(self, master, path):
        tk.Frame.__init__(self, master)
        self.tree = ttk.Treeview(self)
        self.tree.config()
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text=path, anchor='w')
        self.tree["columns"] = ("type")
        self.tree.column("type",width=50)
        self.tree.heading("type", text="Type")

        abspath = os.path.abspath(path)
        # root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory('', abspath)

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

