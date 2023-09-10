import customtkinter 
from threading import Thread
from tkinter import messagebox
class ROMSearchFrame(customtkinter.CTkFrame):
    def __init__(self, master, dolphin, settings):
        super().__init__(master)
        self.master = master 
        self.settings = settings 
        self.dolphin = dolphin 
        self.results_per_page = 4
        self.update_in_progress = False
        self.build_frame()
        
        
   
    def define_roms(self):
        self.roms = self.dolphin.get_downloadable_roms()
        
        if not all(self.roms):
            self.refresh_button.configure(state="normal", text="Refresh")
            messagebox.showerror("Error", self.roms[1])
            return
        self.roms = self.roms[1]
        for widget in (self.refresh_button, self.search_button, self.search_entry, self.prev_button, self.next_button, self.current_page_entry):
            widget.configure(state="normal")
        
        self.searched_roms = self.roms
        self.total_pages = (len(self.searched_roms) + self.results_per_page - 1) // self.results_per_page   
        self.refresh_button.configure(state="disabled", text="refresh")
        self.update_results()
    def get_roms(self):
        self.refresh_button.configure(state="disabled", text="fetching...")
        get_roms_thread = Thread(target=self.define_roms)
        get_roms_thread.start()
        
    def build_frame(self):
        # Create a search bar
        
        refresh_frame = customtkinter.CTkFrame(self, corner_radius=50)
        refresh_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        self.refresh_button = customtkinter.CTkButton(refresh_frame, text="refresh", width=100, command=self.get_roms)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5)
        search_frame = customtkinter.CTkFrame(self, corner_radius=50)
        search_frame.grid(row=0, column=0, pady=(10,0), sticky="ne")

        self.search_entry = customtkinter.CTkEntry(search_frame, state="disabled", placeholder_text="Search")
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.search_button = customtkinter.CTkButton(search_frame, state="disabled", text="Go", width=60, command=self.perform_search)
        self.search_button.grid(row=0, column=1, padx=10, sticky="e", pady=10)

        # Create the middle section with the scrollable frame
        self.result_frame = customtkinter.CTkScrollableFrame(self, width=650, height=20)
        self.result_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        # Create the list of results (you can populate this dynamically)


        # Create labels to display results

        self.current_page = 1
        # Create the bottom section with page navigation
        page_navigation_frame = customtkinter.CTkFrame(self)
        page_navigation_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.prev_button = customtkinter.CTkButton(page_navigation_frame, width=30, state="disabled", text=" < ", command=self.go_to_previous_page)
        self.prev_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create an entry widget for the current page number
        self.current_page_entry = customtkinter.CTkEntry(page_navigation_frame, width=50, state="disabled")
        self.current_page_entry.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.current_page_entry.insert(0, str(self.current_page))  # Set initial value
        self.current_page_entry.bind("<Return>", self.go_to_page)

        self.next_button = customtkinter.CTkButton(page_navigation_frame, state="disabled", width=30, text=" > ", command=self.go_to_next_page)
        self.next_button.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Configure column weights for page_navigation_frame
        page_navigation_frame.grid_columnconfigure(0, weight=1)
        page_navigation_frame.grid_columnconfigure(1, weight=1)
        page_navigation_frame.grid_columnconfigure(2, weight=1)


        # Initial display of results
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
   

    
    
    def go_to_previous_page(self):
        if self.current_page - 1 == 0:
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
            return 
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.go_to_page(None, self.current_page - 1)
        
    def go_to_next_page(self):
        if self.current_page + 1 > self.total_pages:
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
            return
        self.next_button.configure(state="disabled")
        self.prev_button.configure(state="disabled")
        self.go_to_page(None, self.current_page + 1)
        
    def update_results(self):
        if self.update_in_progress:
            return
        self.update_in_progress = True
        start_index = (self.current_page - 1) * self.results_per_page
        end_index = start_index + self.results_per_page
        print(f"Start {start_index}\nend {end_index}")
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        row_counter = 0
        for i, rom in enumerate(self.searched_roms):
            if i > end_index or i < start_index:
                continue
            entry_var = customtkinter.StringVar()
            entry_var.set(rom.filename.replace(".zip", ""))
            entry = customtkinter.CTkEntry(self.result_frame, textvariable=entry_var, state="normal", width=400)
            entry_var.trace("w", callback=lambda var, index, mode, entry_va=entry_var, original=rom.filename.replace(".zip", ""): self.revert_entry(var, index, mode, entry_va, original))

            entry.grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
            button = customtkinter.CTkButton(self.result_frame, text="Download", command = lambda url=rom.url:self.download_rom(url))
            button.grid(row=row_counter, column=1, padx=10, pady=5, sticky="e")
            row_counter += 1
        self.current_page_entry.delete(0, customtkinter.END)
        self.current_page_entry.insert(0, str(self.current_page))
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.update_in_progress = False
    def revert_entry(self, var, index, mode, entry_var, original):
        entry_var.set(original)

    def perform_search(self, event=None):
        # Implement your search logic here
        # Update the 'results' list with the search results
        # Then call self.update_results(results) to display the results
        print("performing search")
        query = self.search_entry.get()
        if query == "":
            self.searched_roms = self.roms
        else:
            self.searched_roms = []
            for rom in self.roms:
                if query.lower() in rom.filename.lower():
                    self.searched_roms.append(rom)
        self.total_pages = (len(self.searched_roms) + self.results_per_page - 1) // self.results_per_page
        self.current_page = 1
        Thread(target=self.update_results).start()

    def go_to_page(self, event=None, page_no=None):
        if self.update_in_progress:
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
            return
            
        try:
            print(f"received page number of {page_no}")
            page_number = int(self.current_page_entry.get()) if page_no is None else int(page_no)
            print(f"defined page_no as {page_number}")
            if page_number == self.current_page:
                print("returning ")
                return
            if 1 <= page_number <= self.total_pages:
                self.current_page = page_number
                self.current_page_entry.delete(0, customtkinter.END)
                self.current_page_entry.insert(0, str(self.current_page))
                print("updating results")
                Thread(target=self.update_results).start()
            else:
                # Display an error message or handle invalid page numbers
                self.current_page_entry.delete(0, customtkinter.END)
                self.current_page_entry.insert(0, str(self.current_page))
                pass
        except ValueError:
            # Handle invalid input (non-integer)
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
            pass
    def download_rom(self, url):
        print("downloading", url)