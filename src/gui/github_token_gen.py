import customtkinter 
from tkinter import messagebox
import requests
import webbrowser 
from threading import Thread
import os 
import time

from utils.auth_token_manager import request_device_code, request_token, write_token_to_file
class GitHubTokenGen(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("GitHub Token Generator")
        self.geometry("500x150")
        self.resizable(False, False)
        self.poll_token = True 
        self.master = master 
        self.token_response = 0
        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()
        self.token_path = os.path.join(os.getenv("APPDATA"), "Emulator Manager", ".token")

    def on_closing(self):
        self.master.token_gen = None 
        self.poll_token = False
        self.destroy()
    def create_widgets(self):
        self.label = customtkinter.CTkLabel(self, text="Click the 'Authorise' button to start the authentication process.")
        self.label.pack(pady=20)
        self.login_button = customtkinter.CTkButton(self, text="Authorise", command=self.start_authentication)
        self.login_button.pack()



    def start_authentication(self):
        self.login_button.configure(state="disabled", text="Authorising...")
        try:
            device_code_response = request_device_code()
            verification_uri = device_code_response["verification_uri"]
            user_code = device_code_response["user_code"]
            device_code = device_code_response["device_code"]
            interval = device_code_response["interval"]
            
            Thread(target=self.copy_and_open_tab, args=(user_code, verification_uri,)).start()
            
            # Poll for the access token
            token_poll_thread = Thread(target=self.poll_for_token, args=(device_code, interval, ))
            token_poll_thread.start()
            self.after(1000, self.check_token_status, token_poll_thread)
        except Exception as error:
            messagebox.showerror("Error", error)
            self.login_button.configure(state="normal", text="Authorise")

    def copy_and_open_tab(self, code, url):
        left=6
        self.label.configure(text=f"You will be redirected to {url}\nPlease enter the code: {code}. It has been copied to your clipboard")
        while left>0:
            if not self.poll_token:
                return
            self.label.configure(text=f"You will be redirected in {left-1} seconds to {url}\nPlease enter the code: {code}. It has been copied to your clipboard")
            time.sleep(1)
            left-=1
        self.label.configure(text=f"You are being redirected to {url}...\nPlease enter the code: {code}. It has been copied to your clipboard")
        self.clipboard_clear()
        self.clipboard_append(code)
        webbrowser.open(url, new=0)
        self.label.configure(text=f"Please enter the code: {code}. It has been copied to your clipboard")
        self.login_button.configure(text="Authorising....")

    

    

    def poll_for_token(self, device_code, interval):
        while self.poll_token:
            try:
                token_response = request_token(device_code)
                if "access_token" in token_response:
                    self.token_response = token_response["access_token"]
                    return
                elif "error" in token_response:
                    error = token_response["error"]
                    if error == "authorization_pending":
   
                        time.sleep(interval)  # Wait for the specified interval
                    elif error == "slow_down":
                        time.sleep(interval+10)  # Wait for interval + 10 seconds
                    else:
                        self.token_response = None
                        return
                else:
                    self.token_response = None 
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Request error: {e}")
                self.token_response = None 
                return
    
    def check_token_status(self, token_poll_thread):
        if token_poll_thread.is_alive():
            # Polling thread is still running, schedule another check
            self.after(1000, self.check_token_status, token_poll_thread)
        else:
            # Polling thread has finished, handle the result
            if self.token_response != 0:
                # Authentication successful
                self.grab_release()
                root_window = self.master.parent_frame.parent_frame
                root_window.deiconify()  # Restore the window if minimized
                root_window.focus_force()  # Bring the window into focus
                root_window.lift()  # Raise the window to the top
                root_window.attributes('-topmost', True)  # Set it as topmost
                root_window.attributes('-topmost', False) 
                messagebox.showinfo("GitHub Authorisation", "Successfully authenticated!")
                write_token_to_file(self.token_response)
                self.master.token_gen = None
                self.destroy()
            else:
                # Authentication failed
                messagebox.showerror("Authentication Error", "Failed to authorize")


   
    
