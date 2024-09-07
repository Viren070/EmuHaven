""" 
This is the ProgressHandler class for the GUI 

For the GUI, our progress handler will be a progress bar that updates as the progress is reported.
The progress handler will have a report_progress method that will have to take the completed_data as an argument.
The report_progress method will then update the progress bar with the new values

We need to create the progress bar class. 
"""
from time import perf_counter
import customtkinter 
from gui.progress_frame import ProgressFrame
from gui.progress_window import ProgressWindow
import queue
from core.utils.logger import Logger

class ProgressHandler:
    def __init__(self, master, type="frame"):
        self.logger = Logger(__name__).get_logger()
        self._progress_bar = ProgressFrame(master, self) if type == "frame" else ProgressWindow(master, self)
        self.master = master
        self.smoothing_factor = 0.3
        self.report_queue = queue.Queue()
        self._operation_start_time = 0
        self._units = ""
        self._total_units = 0
        self._last_speed = 0
        self._average_speed = 0
        self._current_units = 0
        self._should_cancel = False



    def start_operation(self, title, total_units, units, status="Starting..."):

        self._average_speed = 0
        self._total_units = total_units
        self._should_cancel = False
        self._units = units
        self._current_units = 0
        self._last_speed = 0
        self._operation_start_time = perf_counter()
        self._progress_bar.set_eta("00:00:00")
        self._progress_bar.set_title(title)
        self._progress_bar.set_status(status)
        self._progress_bar.update_progress(0, total_units, units)
        self._progress_bar.set_speed(0, units)
        self._progress_bar.set_cancel_button_state("normal")
        self._progress_bar.grid(row=0, column=0, sticky="ew")

        
    def is_total_units_set(self):
        return self._total_units > 0

    def set_total_units(self, total_units):
        self._total_units = total_units
        self._progress_bar.update_progress(self._current_units, total_units, self._units)


    def _process_report(self, report):
        match report["type"]:
            case "progress":
                self._handle_progress_report(report)
            case "success":
                self._handle_success_report(report)
            case "error":
                self._handle_error_report(report)
            case "configure":
                self._handle_configure_report(report)
            
    def _handle_progress_report(self, report):
        """
        {
            "type": "progress",
            "completed_units": x,
        }
        """
        completed_units = report["completed_units"]
        self._current_units = completed_units
        # update progress bar, percentage and progress label
        
        self._progress_bar.update_progress(completed_units, self._total_units, self._units)
        
        # calculate download speed
        last_speed = completed_units / (
            (perf_counter() - self._operation_start_time)
        )
        # use exponential moving average to calculate download speed
        self._average_speed = (
            self.smoothing_factor * last_speed +

            (1 - self.smoothing_factor) * self._average_speed
        )
        self._progress_bar.set_speed(self._average_speed, self._units)
        
        # calculate time left
        if self._average_speed != 0:
            time_left = (self._total_units - completed_units) / self._average_speed
            minutes, seconds = divmod(int(time_left), 60)
            hours, minutes = divmod(minutes, 60)
            time_left_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_left_str = "00:00:00"
        self._progress_bar.set_eta(time_left_str)
        
    
    def _handle_success_report(self, report):
        self._should_cancel = True
        self.cancel()
        
    
    def _handle_error_report(self, report):
        self._should_cancel = True
        self.cancel()

    
    def _handle_configure_report(self, report):
        match report["widget"]:
            case "status":
                self._progress_bar.set_status(report["kwargs"]["text"])
            case "cancel_button":
                self._progress_bar.set_cancel_button_state(report["kwargs"]["state"])
            
    
    def report_progress(self, completed_units):
        self._handle_progress_report({"completed_units": completed_units})
    
    def report_success(self):
        self._handle_success_report({})
        
    def report_error(self, error):
        self._handle_error_report({"error": error})
        
    
    def report_configure(self, widget, **kwargs):
        self.report_queue.put({"type": "configure", "widget": widget, "kwargs": kwargs})
        
    def set_cancel_button_state(self, state):
        self._progress_bar.set_cancel_button_state(state)

    def should_cancel(self):
        return self._should_cancel

    def send_cancel_signal_to_operation(self):
        """
        called by external events like cancel buttons to signal the operation to cancel
        """
        self._should_cancel = True
        self.set_cancel_button_state("disabled")
       
    
    def cancel(self):
        """
        called by the operation
        """
        self._progress_bar.grid_forget()

