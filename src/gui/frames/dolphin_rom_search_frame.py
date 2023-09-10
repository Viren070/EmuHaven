import customtkinter 
from threading import Thread
from tkinter import messagebox
import os 
from utils.downloader import download_through_stream
from utils.requests_utils import create_get_connection, get_headers
class ROMSearchFrame(customtkinter.CTkFrame):
    def __init__(self, master, dolphin, settings):
        super().__init__(master)
        self.master = master 
        self.settings = settings 
        self.dolphin = dolphin 
        self.results_per_page = 10
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
     
            entry = customtkinter.CTkEntry(self.result_frame, width=400)
            entry.insert(0, rom.filename.replace(".zip", ""))
            entry.configure(state="disabled")
            progress_bar = customtkinter.CTkProgressBar(self.result_frame, mode="determinate")
            
            entry.grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
            button = customtkinter.CTkButton(self.result_frame, text="Download")
            button.configure(command = lambda rom=rom, progress_bar=progress_bar, button=button, row=row_counter+1:self.download_rom_event(rom, progress_bar, row, button))
            button.grid(row=row_counter, column=1, padx=10, pady=5, sticky="e")
            row_counter += 2
        self.current_page_entry.delete(0, customtkinter.END)
        self.current_page_entry.insert(0, str(self.current_page))
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.update_in_progress = False


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
            page_number = int(self.current_page_entry.get()) if page_no is None else int(page_no)
            if page_number == self.current_page:
                return
            if 1 <= page_number <= self.total_pages:
                self.current_page = page_number
                self.current_page_entry.delete(0, customtkinter.END)
                self.current_page_entry.insert(0, str(self.current_page))
                Thread(target=self.update_results).start()
            else:
                # Display an error message or handle invalid page numbers
                self.current_page_entry.delete(0, customtkinter.END)
                self.current_page_entry.insert(0, str(self.current_page))
        except ValueError:
            # Handle invalid input (non-integer)
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
    def download_rom_event(self, rom, progress_bar, row, button):
        Thread(target=self.download_rom_handler, args=(rom, progress_bar, row, button)).start()
    def download_rom_handler(self, rom, progress_bar, row, button):
        button.configure(state="disabled")
        download_result = self.download_rom(rom, progress_bar, row)
        button.configure(state="normal")
    def download_rom(self, rom, progress_bar, row):
        download_folder = self.settings.dolphin.rom_directory
        download_path = os.path.join(download_folder, rom.filename)
        response = create_get_connection(rom.url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response):
            return response 
        response = response[1]
        progress_bar.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        download_result = download_through_stream(response, download_path, progress_bar, 1024*203, total_size=int(response.headers.get('content-length', 0)), custom=False)
        return (True,download_result)