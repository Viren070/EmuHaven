import customtkinter
from time import perf_counter
from tkinter import messagebox
class ProgressFrame(customtkinter.CTkFrame):
    def __init__(self, parent_frame, filename):
        super().__init__(parent_frame)
        self.grid_columnconfigure(0, weight=1)
        self.cancel_download_raised = False
        self.filename = filename
        self.start_time = perf_counter()

        self.total_size = 0
        self.time_during_cancel = 0
        self._current_width = 200
        self.download_name = customtkinter.CTkLabel(self, text=filename)
        self.download_name.grid(row=0, column=0, sticky="W", padx=10, pady=5)

        self.progress_label = customtkinter.CTkLabel(self, text="0 MB / 0 MB")
        self.progress_label.grid(row=1, column=0, sticky="W", padx=10)

        self.progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate"
        )
        self.progress_bar.grid(
            row=2, column=0, columnspan=6, padx=(10, 45), pady=5, sticky="EW"
        )
        self.progress_bar.set(0)

        self.percentage_complete = customtkinter.CTkLabel(self, text="0%")
        self.percentage_complete.grid(row=2, column=5, sticky="E", padx=10)

        self.download_speed_label = customtkinter.CTkLabel(self, text="0 MB/s")
        self.download_speed_label.grid(row=1, column=5, sticky="E", padx=10)

        self.install_status_label = customtkinter.CTkLabel(
            self, width=100, text="Status: Downloading..."
        )
        self.install_status_label.grid(row=3, column=0, sticky="W", padx=10, pady=5)

        self.eta_label = customtkinter.CTkLabel(self, text="Time Left: 00:00:00")
        self.eta_label.grid(row=0, column=5, sticky="E", pady=5, padx=10)

        self.cancel_download_button = customtkinter.CTkButton(
            self, text="Cancel", command=self.cancel_button_event
        )
        self.cancel_download_button.grid(row=3, column=5, pady=10, padx=10, sticky="E")

    def update_download_progress(self, downloaded_bytes, chunk_size):
        done = downloaded_bytes / self.total_size
        avg_speed = downloaded_bytes / (
            (perf_counter() - self.start_time) - self.time_during_cancel
        )
        # cur_speed = chunk_size / (perf_counter() - self.time_at_start_of_chunk)
        time_left = (self.total_size - downloaded_bytes) / avg_speed

        minutes, seconds = divmod(int(time_left), 60)
        hours, minutes = divmod(minutes, 60)
        time_left_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.progress_bar.set(done)
        self.progress_label.configure(
            text=f"{downloaded_bytes/1024/1024:.2f} MB / {self.total_size/1024/1024:.2f} MB"
        )
        self.percentage_complete.configure(text=f"{str(done*100).split('.')[0]}%")
        self.download_speed_label.configure(text=f"{avg_speed/1024/1024:.2f} MB/s")
        self.eta_label.configure(text=f"Time Left: {time_left_str}")
        self.time_at_start_of_chunk = perf_counter()
        if self.install_status_label.cget("text") != "Status: Downloading...":
            self.install_status_label.configure(text="Status: Downloading...")
        # print(f"Current: {speed/1024/1024:.2f} MB/s")
        # print(f"Avg: {avg_speed/1024/1024:.2f} MB/s")

    def cancel_button_event_old(self, skip_confirmation=False):
        start_time = perf_counter()
        self.cancel_download_raised = True
        self.install_status_label.configure(text="Status: Cancelling...")
        if skip_confirmation and messagebox.askyesno(
            "Confirmation", "Are you sure you want to cancel this download?"
        ):
            self.install_status_label.configure(text="Status: Cancelled")
            return True
        else:
            self.time_during_cancel += perf_counter() - start_time
            return False

    def cancel_button_event(self):
        start_time = perf_counter()

        if messagebox.askyesno(
            "Confirmation", "Are you sure you want to cancel this download?"
        ):
            self.install_status_label.configure(text="Status: Cancelled")
            self.cancel_download_raised = True
            return True
        else:
            self.time_during_cancel += perf_counter() - start_time
            return False

    def remove_status_frame(self):
        self.destroy()

    def update_extraction_progress(self, value):
        self.progress_bar.set(value)
        self.percentage_complete.configure(text=f"{str(value*100).split('.')[0]}%")

    def installation_interrupted(self, error):
        self.cancel_download_raised = True
        self.cancel_download_button.configure(state="disabled")
        self.install_status_label.configure(text=f"Encountered error: {error}")
        self.cancel_download_button.configure(
            text="Remove", command=self.remove_status_frame, state="normal"
        )

    def skip_to_installation(self):
        self.download_speed_label.grid_forget()
        self.eta_label.grid_forget()
        self.cancel_download_button.configure(state="disabled")
        self.progress_label.grid_forget()

    def complete_download(self, emulator=None, text=None):
        self.cancel_download_button.configure(state="disabled")
        self.install_status_label.configure(
            text=f"Status: Installing for {emulator}...." if not emulator else text
        )
        self.progress_bar.set(0)
        self.percentage_complete.configure(text="0%")
    def update_status_label(self, text):
        self.install_status_label.configure(text=text)
    def finish_installation(self):
        minutes, seconds = divmod(int(perf_counter() - self.start_time), 60)
        hours, minutes = divmod(minutes, 60)
        elapsed_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.install_status_label.configure(text="Status: Complete")
        self.eta_label.configure(text=f"Elapsed time: {elapsed_time}")
        self.download_speed_label.configure(text="0 MB/s")
        self.cancel_download_button.configure(
            text="Remove", command=self.remove_status_frame, state="normal"
        )
        messagebox.showinfo("Download Complete", f"{self.filename} has been installed")
