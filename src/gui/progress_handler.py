""" 
This is the ProgressHandler class for the GUI 

For the GUI, our progress handler will be a progress bar that updates as the progress is reported.
The progress handler will have a report_progress method that will have to take the completed_data as an argument.
The report_progress method will then update the progress bar with the new values

We need to create the progress bar class. 
"""
from time import perf_counter
import customtkinter 

class ProgressHandler:
    def __init__(self, parent):
        self._progress = 0 
        self._total = 0
        self._completed = False
        self._cancel_flag = False
        self._status = "Idle"
        self._title = "Operation Title"
        self._total_data = 0
        self._completed_data = 0
        self._percentage_completed = 0
        self._units = "Data Units"
        self._speed = 0
        self._time_remaining = 0
        self.smoothing_factor = 0.3
        self.cancel_download_raised = False
        self.start_time = perf_counter()
        self.filename = None
        self.total_size = 0
        self.progress_bar.time_during_cancel = 0
        
        self.initialise_progress_bar(parent)
        
    def initialise_progress_bar(self, parent):
        self.progress_bar = customtkinter.CTkFrame(parent)
        self.progress_bar.grid_columnconfigure(0, weight=1)

        self.progress_bar.configure(width=200)
        self.progress_bar.download_name = customtkinter.CTkLabel(self)
        self.progress_bar.progress_label = customtkinter.CTkLabel(self)
        self.progress_bar.progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate"
        )
        self.progress_bar.percentage_complete = customtkinter.CTkLabel(self, text="0%")
        self.progress_bar.download_speed_label = customtkinter.CTkLabel(self, text="0 MB/s")

        self.progress_bar.install_status_label = customtkinter.CTkLabel(
            self, width=100, text="Status: Downloading..."
        )
        self.progress_bar.eta_label = customtkinter.CTkLabel(self, text="Time Left: 00:00:00")
        self.progress_bar.cancel_download_button = customtkinter.CTkButton(
            self, text="Cancel", command=self.cancel_button_event
        )
        
    def cancel_button_event(self):
        self.cancel_download_raised = True
        self.progress_bar.cancel_download_button.configure(state="disabled", text="Cancelling...")
