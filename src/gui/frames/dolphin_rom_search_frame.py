import customtkinter 
from threading import Thread
from tkinter import messagebox
from zipfile import ZipFile
import os 
from utils.downloader import download_through_stream
from utils.requests_utils import create_get_connection, get_headers
from gui.frames.progress_frame import ProgressFrame
class SearchFrame(customtkinter.CTkFrame):
    def __init__(self, master, root, console):
        super().__init__(master, height=700)
        self.results_per_page = 15
        self.console = console 
        self.root = root
        self.dolphin = root.dolphin 
        self.update_in_progress = False
        self.build_frame()
    def get_roms(self):
        self.refresh_button.configure(state="disabled", text="Fetching...")
        get_roms_thread = Thread(target=self.define_roms)
        get_roms_thread.start()
    def define_roms(self):
        self.roms = self.dolphin.get_downloadable_roms(self.console)
        
        if not all(self.roms):
            self.refresh_button.configure(state="normal", text="Refresh")
            messagebox.showerror("Error", self.roms[1])
            return
        self.roms = self.roms[1]
        for widget in (self.refresh_button, self.search_button, self.search_entry, self.prev_button, self.next_button, self.current_page_entry):
            widget.configure(state="normal")
        
        self.searched_roms = self.roms
        self.total_pages = (len(self.searched_roms) + self.results_per_page - 1) // self.results_per_page   
        self.total_pages_label.configure(text=f"/ {self.total_pages}")
        self.refresh_button.grid_forget()
        self.refresh_frame.grid_forget()
        self.update_results()
    def build_frame(self):
        # Create a search bar
        
        self.refresh_frame = customtkinter.CTkFrame(self, corner_radius=50)
        self.refresh_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        self.refresh_button = customtkinter.CTkButton(self.refresh_frame, text="Fetch ROMs", width=100, command=self.get_roms)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5)
        search_frame = customtkinter.CTkFrame(self, corner_radius=50)
        search_frame.grid(row=0, column=0, pady=(10,0), sticky="ne")

        self.search_entry = customtkinter.CTkEntry(search_frame, state="disabled", placeholder_text="Search")
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.search_button = customtkinter.CTkButton(search_frame, state="disabled", text="Go", width=60, command=self.perform_search)
        self.search_button.grid(row=0, column=1, padx=10, sticky="e", pady=10)

        # Create the middle section with the scrollable frame
        self.result_frame = customtkinter.CTkScrollableFrame(self, width=650, height=20)
        self.result_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        # Create the list of results (you can populate this dynamically)


        # Create labels to display results

        self.current_page = 1
        # Create the bottom section with page navigation

        # Adjust the width of the page navigation buttons
        button_width = 40  # You can adjust this width as needed

        # Create an entry widget for the current page number and the label for total pages
        page_navigation_frame = customtkinter.CTkFrame(self)
        page_navigation_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Create a left frame for the entry widget and label
        left_frame = customtkinter.CTkFrame(page_navigation_frame)
        left_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")

        # Create an entry widget for the current page number
        self.current_page_entry = customtkinter.CTkEntry(left_frame, width=40, state="disabled")
        self.current_page_entry.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")
        self.current_page_entry.insert(0, str(self.current_page))  # Set initial value
        self.current_page_entry.bind("<Return>", self.go_to_page)

        # Label to display total pages
        self.total_pages_label = customtkinter.CTkLabel(left_frame, text="/ ")
        self.total_pages_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create a right frame for the previous and next buttons
        right_frame = customtkinter.CTkFrame(page_navigation_frame)
        right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")

        # Adjust the width of the page navigation buttons
        button_width = 50  # You can adjust this width as needed

        self.prev_button = customtkinter.CTkButton(right_frame, width=button_width, state="disabled", text=" < ", command=self.go_to_previous_page)
        self.prev_button.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.next_button = customtkinter.CTkButton(right_frame, state="disabled", width=button_width, text=" > ", command=self.go_to_next_page)
        self.next_button.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # Configure column weights for page_navigation_frame
        page_navigation_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(1, weight=0)  # Adjust weight for label
        right_frame.grid_columnconfigure(0, weight=0)  # Adjust weight for buttons
        right_frame.grid_columnconfigure(1, weight=0)



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
            self.next_button.configure(state="normal")
            self.prev_button.configure(state="normal")
            return
        self.update_in_progress = True
        start_index = (self.current_page - 1) * self.results_per_page
        end_index = start_index + self.results_per_page
        for widget in self.result_frame.winfo_children():
            widget.grid_forget()
            
        row_counter = 0
        for i, rom in enumerate(self.searched_roms):
            if i > end_index or i < start_index:
                continue
     
            entry = customtkinter.CTkEntry(self.result_frame, width=400)
            entry.insert(0, rom.filename.replace(".zip", ""))
            entry.configure(state="disabled")
            
            entry.grid(row=row_counter, column=0, padx=10, pady=5, sticky="w")
            button = customtkinter.CTkButton(self.result_frame, text="Download")
            button.configure(command = lambda button=button, rom=rom:self.root.download_rom_event(rom, button))
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
        query = self.search_entry.get()
        if query == "":
            self.searched_roms = self.roms
        else:
            self.searched_roms = []
            for rom in self.roms:
                if query.lower() in rom.filename.lower():
                    self.searched_roms.append(rom)
        self.total_pages = (len(self.searched_roms) + self.results_per_page - 1) // self.results_per_page
        self.total_pages_label.configure(text=f"/ {self.total_pages}")
        self.current_page = 1
        Thread(target=self.update_results).start()

    def go_to_page(self, event=None, page_no=None):
        if self.update_in_progress:
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
            self.next_button.configure(state="normal")
            self.prev_button.configure(state="normal")
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
            
            
            
            
            
            
            
            
class ROMSearchFrame(customtkinter.CTkTabview):
    def __init__(self, master, dolphin, settings):
        super().__init__(master, height=500, width=700)
        self.master = master 
        self.settings = settings 
        self.dolphin = dolphin 
        self.results_per_page = 10
        self.update_in_progress = False
        self.downloads_in_progress = 0
        self.build_frame()
        
        
    def build_frame(self):

        self.grid(row=0, column=0, sticky="nsew")
        self.add("Wii ROMs")
        self.add("GameCube ROMs")
        self.add("Downloads")
        self.tab("Wii ROMs").grid_columnconfigure(0, weight=1)
        self.tab("Wii ROMs").grid_rowconfigure(0, weight=1)
        self.tab("GameCube ROMs").grid_columnconfigure(0, weight=1)
        self.tab("GameCube ROMs").grid_rowconfigure(0, weight=1)
        self.tab("Downloads").grid_columnconfigure(0, weight=1)
        self.tab("Downloads").grid_rowconfigure(0, weight=1)
        self.wii_roms_frame = SearchFrame(self.tab("Wii ROMs"), self, "wii",)
        self.wii_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.gamecube_roms_frame = SearchFrame(self.tab("GameCube ROMs"), self, "gamecube")
        self.gamecube_roms_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.downloads_frame = customtkinter.CTkScrollableFrame(self.tab("Downloads"))
        self.downloads_frame.grid_columnconfigure(0, weight=1)
        self.downloads_frame.grid(row=0, column=0, sticky="nsew")
    
   
        
    
    def download_rom_event(self, rom, button):
        Thread(target=self.download_rom_handler, args=(rom, button)).start()
    def download_rom_handler(self, rom, button):
        self.downloads_in_progress += 1
        button.configure(state="disabled", text="Downloading...")
        self.set("Downloads")
        download_result = self.download_rom(rom)
        if not all(download_result):
            if download_result[1] != "Cancelled":
                messagebox.showerror("Error", f"An error occurred while attempting to download this ROM\n\n{download_result[1]}")
            else:
                os.remove(download_result[2])
            self.downloads_in_progress -= 1
            button.configure(state="normal", text="Download")
            return 
        extract_result = self.extract_rom(download_result[1])
        if not all(extract_result):
            messagebox.showerror("Error", f"An error occurred while attempting to extract this ROM\n\n{extract_result[1]}")
            button.configure(state="normal", text="Download")
        if self.settings.app.delete_files == "True":
            if os.path.exists(download_result[1]):
                os.remove(download_result[1])
        messagebox.showinfo("ROM Install", f"The ROM was successfully installed at path: \n\n{extract_result[1]}")
        button.configure(state="normal", text="Download")
    def download_rom(self, rom):
        download_folder = self.settings.dolphin.rom_directory
        download_path = os.path.join(download_folder, rom.filename)
        response = create_get_connection(rom.url, stream=True, headers=get_headers(self.settings.app.token), timeout=30)
        if not all(response):
            return response 
        response = response[1]
        progress_frame = ProgressFrame(self.downloads_frame, rom.filename)
        progress_frame.total_size = int(response.headers.get("content-length", 0))
        progress_frame.grid(row=self.downloads_in_progress, column=0, padx=10,pady=10, sticky="ew")
        download_result = download_through_stream(response, download_path, progress_frame, 1024*203, total_size=int(response.headers.get('content-length', 0)))
        progress_frame.destroy()
        return download_result
    def extract_rom(self, path_to_rom_archive):
        try:
            with ZipFile(path_to_rom_archive, 'r') as zip_ref:

                file_list = zip_ref.namelist()
                if len(file_list) != 1:
                    return (False, "Unexpected number of files")

                extracted_file_name = file_list[0]
                extracted_file_path = os.path.join(self.settings.dolphin.rom_directory, extracted_file_name)
                zip_ref.extract(extracted_file_name, self.settings.dolphin.rom_directory)

                return (True, extracted_file_path)

        except Exception as error:
            return (False, error)

       