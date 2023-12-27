import os
from tkinter import filedialog, messagebox
from customtkinter import CTkToplevel, CTkEntry, CTkButton, CTkCheckBox, CTkScrollableFrame, CTkFrame

class FolderSelector(CTkToplevel):
    def __init__(self, *args, title, predefined_directory=None, allowed_folders=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.populating = False
        self.predefined_directory = predefined_directory
        self.allowed_folders = allowed_folders

        # Central frame
        self.title(title)
        self.geometry("700x500")
        self.central_frame = CTkFrame(self)
        self.central_frame.grid(row=0, column=0, sticky='nsew')

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)  # Central frame gets all the available vertical space
        self.grid_columnconfigure(0, weight=1)  # Central frame gets all the available horizontal space
        self.central_frame.grid_rowconfigure(1, weight=1)  # Scrollable frame gets all the available vertical space
        self.central_frame.grid_columnconfigure(0, weight=2)  # Entry widget gets 2 parts of the available space
        self.central_frame.grid_columnconfigure(1, weight=1)  # Browse button gets 1 part of the available space

        # Checkbuttons
        self.checkbuttons = []
        
        # Entry and Browse button
        self.entry = CTkEntry(self.central_frame)
        self.entry.grid(row=0, column=0, sticky='ew', padx=(20,10), pady=10)  # Increase padx and pady
        self.entry.bind('<Return>', lambda e: self.populate_checkbuttons(self.entry.get()))
        self.browse_button = CTkButton(self.central_frame, text="Browse", command=self.browse)
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)  # Increase padx and pady


        # Scrollable frame for Checkbuttons
        self.scroll_frame = CTkScrollableFrame(self.central_frame)
        self.scroll_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)  # Increase padx and pady


        # Frame for OK and Cancel buttons
        self.button_frame = CTkFrame(self.central_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)  # Increase padx and pady

        # OK and Cancel buttons
        self.ok_button = CTkButton(self.button_frame, text="OK", command=self.ok)
        self.ok_button.pack(side='left', padx=10, pady=10)  # Increase padx and pady
        self.cancel_button = CTkButton(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side='right', padx=10, pady=10)  # Increase padx and pady

        # Disable entry and browse button if predefined_directory is not None
        if self.predefined_directory is not None:
            self.entry.insert(0, self.predefined_directory)
            self.entry.configure(state='disabled')
            self.browse_button.configure(state='disabled')
            self.populate_checkbuttons(self.predefined_directory)
        self.result = None

    def browse(self):
        directory = filedialog.askdirectory()
        self.entry.delete(0, 'end')
        self.entry.insert(0, directory)
        self.populate_checkbuttons(directory)

    def populate_checkbuttons(self, directory):
        if self.populating or directory == "" or not os.path.isdir(directory) or not os.path.exists(directory):
            return
        self.populating = True
        # Remove old checkbuttons
        for cb in self.checkbuttons:
            cb.pack_forget()
        self.checkbuttons.clear()

        # Add new checkbuttons
        for name in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, name)):
                cb = CTkCheckBox(self.scroll_frame, text=name)
                cb.pack(side='top', fill='x', pady=5)
                # Disable checkbox if allowed_folders is not None and name is not in allowed_folders
                if self.allowed_folders is not None and name not in self.allowed_folders:
                    cb.configure(state='disabled')
                self.checkbuttons.append(cb)
        self.populating = False
        
        
    def ok(self):
        self.result = [cb.cget('text') for cb in self.checkbuttons if cb.get()]
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

