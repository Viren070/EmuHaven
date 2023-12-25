import os
from tkinter import filedialog
from customtkinter import CTkToplevel, CTkEntry, CTkButton, CTkCheckBox, CTkScrollableFrame, CTkFrame

class FolderSelector(CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Central frame
        self.central_frame = CTkFrame(self)
        self.central_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Configure grid weights
        self.central_frame.grid_columnconfigure(0, weight=2)  # Entry widget gets 2 parts of the available space
        self.central_frame.grid_columnconfigure(1, weight=1)  # Browse button gets 1 part of the available space
        self.central_frame.grid_rowconfigure(1, weight=1)  # Scrollable frame gets all the available vertical space

        # Increase the size of the central frame
        self.central_frame.configure(width=600, height=400)

        # Entry and Browse button
        self.entry = CTkEntry(self.central_frame)
        self.entry.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.browse_button = CTkButton(self.central_frame, text="Browse", command=self.browse)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        # Scrollable frame for Checkbuttons
        self.scroll_frame = CTkScrollableFrame(self.central_frame)
        self.scroll_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

        # Checkbuttons
        self.checkbuttons = []

        # Frame for OK and Cancel buttons
        self.button_frame = CTkFrame(self.central_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # OK and Cancel buttons
        self.ok_button = CTkButton(self.button_frame, text="OK", command=self.ok)
        self.ok_button.pack(side='left', padx=5, pady=5)
        self.cancel_button = CTkButton(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side='right', padx=5, pady=5)

        self.result = None

    def browse(self):
        directory = filedialog.askdirectory()
        self.entry.delete(0, 'end')
        self.entry.insert(0, directory)
        self.populate_checkbuttons(directory)

    def populate_checkbuttons(self, directory):
        # Remove old checkbuttons
        for cb in self.checkbuttons:
            cb.pack_forget()
        self.checkbuttons.clear()

        # Add new checkbuttons
        for name in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, name)):
                cb = CTkCheckBox(self.scroll_frame, text=name)
                cb.pack(side='top', fill='x')
                self.checkbuttons.append(cb)

    def ok(self):
        self.result = [cb.cget('text') for cb in self.checkbuttons if cb.get()]
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

# Usage
import tkinter as tk
root = tk.Tk()
fs = FolderSelector(root)
root.mainloop()
print(fs.result)