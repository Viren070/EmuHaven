import webbrowser
from threading import Thread

import customtkinter

from core.config import constants
from core.network.myrient import get_list_of_games
from gui.handlers.thread_event_manager import ThreadEventManager
from core.logging.logger import Logger
from gui.libs import messagebox




class GameListFrame(customtkinter.CTkFrame):
    def __init__(self, master, event_manager: ThreadEventManager):
        super().__init__(master, height=700)
        self.logger = Logger(__name__).get_logger()
        self.update_in_progress = False
        self.event_manager = event_manager
        self.total_pages = 0
        self.current_page = 1
        self.game_list = []
        self.searched_games = []
        self.build_frame()
        
    def configure_widgets(self, fetch_button_text="Get Games", state="disabled"):
        self.refresh_button.configure(state=state, text=fetch_button_text)
        self.search_entry.configure(state=state)
        self.search_button.configure(state=state)
        self.current_page_entry.configure(state=state)
        self.prev_button.configure(state=state)
        self.next_button.configure(state=state)

    def get_game_list_button_event(self, *args, ignore_messages=True):
        self.configure_widgets(fetch_button_text="Fetching...")
        self.event_manager.add_event(
            event_id="get_games",
            func=self.get_game_list,
            kwargs={},
            completion_functions=[lambda: self.configure_widgets(state="normal")],
            completion_funcs_with_result=[self.process_game_list],
            error_functions=[lambda: messagebox.showerror(self.winfo_toplevel(), "Error", "Failed to fetch games.")],
            ignore_messages=ignore_messages
        )
        
    def get_game_list(self):
        return {
            "result": [],
            "message": {
                "function": messagebox.showerror,
                "args": ("Error", "Game Fetch not implemented.")
            }
        }
        
    def process_game_list(self, game_list):
        self.logger.debug(f"Processing received game list of length {len(game_list)}")
        self.game_list = game_list
        self.searched_games = game_list
        self.total_pages = (len(game_list) + constants.App.RESULTS_PER_GAME_PAGE.value - 1) // constants.App.RESULTS_PER_GAME_PAGE.value
        self.total_pages_label.configure(text=f"/ {self.total_pages}")
        self.update_results()
        self.logger.debug("Game list processed")

    def build_frame(self):
        # Create a search bar
        self.refresh_frame = customtkinter.CTkFrame(self, corner_radius=50)
        self.refresh_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        self.refresh_button = customtkinter.CTkButton(self.refresh_frame, text="Get Games", width=100, corner_radius=50, command=self.get_game_list_button_event)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5)

        search_frame = customtkinter.CTkFrame(self, corner_radius=50)
        search_frame.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="ne")

        self.search_entry = customtkinter.CTkEntry(search_frame, state  ="disabled", placeholder_text="Search")
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.search_entry.bind("<Return>", self.perform_search)
        self.search_button = customtkinter.CTkButton(search_frame, state="disabled", text="Go", width=60, command=self.perform_search)
        self.search_button.grid(row=0, column=1, padx=10, sticky="e", pady=10)

        self.result_frame = customtkinter.CTkScrollableFrame(self, width=650, height=20)
        self.result_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.current_page = 1

        page_navigation_frame = customtkinter.CTkFrame(self)
        page_navigation_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        left_frame = customtkinter.CTkFrame(page_navigation_frame)
        left_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")

        self.current_page_entry = customtkinter.CTkEntry(left_frame, width=40, state="disabled")
        self.current_page_entry.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsew")
        self.current_page_entry.insert(0, str(self.current_page))  # Set initial value
        self.current_page_entry.bind("<Return>", self.go_to_page)

        self.total_pages_label = customtkinter.CTkLabel(left_frame, text="/ ")
        self.total_pages_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        right_frame = customtkinter.CTkFrame(page_navigation_frame)
        right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")

        button_width = 50

        self.prev_button = customtkinter.CTkButton(right_frame, width=button_width, state="disabled", text=" < ", command=self.go_to_previous_page)
        self.prev_button.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        self.next_button = customtkinter.CTkButton(right_frame, state="disabled", width=button_width, text=" > ", command=self.go_to_next_page)
        self.next_button.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        page_navigation_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_columnconfigure(1, weight=0)  # Adjust weight for label
        right_frame.grid_columnconfigure(0, weight=0)  # Adjust weight for buttons
        right_frame.grid_columnconfigure(1, weight=0)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=10)

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
        start_index = (self.current_page - 1) * constants.App.RESULTS_PER_GAME_PAGE.value
        end_index = (start_index + constants.App.RESULTS_PER_GAME_PAGE.value) - 1
        for widget in self.result_frame.winfo_children():
            widget.grid_forget()

        row_counter = 0
        for i, game in enumerate(self.searched_games):
            if i > end_index:
                break
            if i < start_index:
                continue
            self.add_game_to_frame(game, row_counter)
            row_counter += 2
        
        self.current_page_entry.configure(state="normal")
        self.current_page_entry.delete(0, customtkinter.END)
        self.current_page_entry.insert(0, str(self.current_page))
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.update_in_progress = False
        
    def add_game_to_frame(self, game, row_counter):
        customtkinter.CTkLabel(self.result_frame, text=game).grid(row=row_counter, column=0, padx=5, pady=5, sticky="ew")

    def perform_search(self, *args):
        query = self.search_entry.get()
        if query == "":
            self.searched_games = self.game_list
        else:
            self.searched_games = []
            for game in self.game_list:
                if query.lower() in game.lower():
                    self.searched_games.append(game)
        self.total_pages = (len(self.searched_games) + constants.App.RESULTS_PER_GAME_PAGE.value - 1) // constants.App.RESULTS_PER_GAME_PAGE.value
        self.total_pages_label.configure(text=f"/ {self.total_pages}")
        self.current_page = 1
        self.update_results()

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
                self.update_results()
            else:
                # Display an error message or handle invalid page numbers
                self.current_page_entry.delete(0, customtkinter.END)
                self.current_page_entry.insert(0, str(self.current_page))
        except ValueError:
            # Handle invalid input (non-integer)
            self.current_page_entry.delete(0, customtkinter.END)
            self.current_page_entry.insert(0, str(self.current_page))
