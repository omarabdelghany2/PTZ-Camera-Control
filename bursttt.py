import obsws_python as obs
import toml
import time
from datetime import datetime
import os
import requests
import tkinter as tk
from tkinter import messagebox, ttk,filedialog
import threading
import webbrowser  # Import the webbrowser module


class ConfigGUI:
    def __init__(self, root, stop_event):
        self.root = root
        self.stop_event = stop_event  # Store stop_event to pass it later
        self.root.title("Configuration Wizard")
        self.root.geometry("400x300")

        # Set background color to match the main GUI
        self.root.configure(bg="#2c3e50")  

        self.config_data = {}  # Dictionary to store config data from all pages
        self.current_page = 0  # Track the current page in the wizard
        self.config_file_path = "config.toml"
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize each page as a method
        self.pages = [self.page_server_info, self.page_screenshot_settings, self.page_folders]

        # Set up button styles to match OBSControllerGUI
        self.style = ttk.Style()
        self.style.configure("TButton",
                             background="#34495e",  # Dark button color
                             foreground="#1c2833",  # Even darker button text color (very dark gray)
                             borderwidth=2,          # Border width
                             relief="flat")          # Flat relief to match the main GUI

        # Display the first page
        self.pages[self.current_page]()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def clear_page(self):
        # Remove all widgets on the current page
        for widget in self.root.winfo_children():
            widget.destroy()

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.pages[self.current_page]()
        else:
            self.save_config()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.pages[self.current_page]()

    def start_main_app(self):
        self.root.quit()  # Close the config GUI
        run_main_app(self.stop_event, self)  # Pass self (the ConfigGUI instance) to the main app

    def load_previous_config(self):
        if os.path.exists(self.config_file_path):
            try:
                self.config_data = toml.load(self.config_file_path)
                # Notify the user that the configuration was loaded successfully
                self.root.after(0, lambda: messagebox.showinfo("Loaded", "Previous configuration loaded successfully."))
                # Close the config GUI and start the main app
                self.root.after(0, self.start_main_app)  
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load configuration: {e}"))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No previous configuration found."))

    def page_server_info(self):
        self.clear_page()

        # Server Info Page
        tk.Label(self.root, text="Camera & Server Information", bg="#2c3e50", fg="white").pack(pady=10)
        tk.Label(self.root, text="Camera IP:", bg="#2c3e50", fg="white").pack()
        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.pack(pady=5)

        tk.Label(self.root, text="OBS WebSocket Port:", bg="#2c3e50", fg="white").pack()
        self.port_entry = tk.Entry(self.root)
        self.port_entry.pack(pady=5)

        tk.Label(self.root, text="WebSocket Password:", bg="#2c3e50", fg="white").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        # "Load Previous Configuration" button
        ttk.Button(self.root, text="Load Previous Configuration", command=self.load_previous_config).pack(pady=10)

        ttk.Button(self.root, text="Next", command=self.save_server_info).pack(pady=10)

    def save_server_info(self):
        # Save server data
        self.config_data["screenshot"] = {
            "ip": self.ip_entry.get(),
            "OBS_WEBSOCKET_PORT": int(self.port_entry.get()),
            "WEBSOCKET_PASSWORD": self.password_entry.get()
        }
        self.next_page()

    def page_screenshot_settings(self):
        self.clear_page()

        # Screenshot Settings Page
        tk.Label(self.root, text="Screenshot Settings", bg="#2c3e50", fg="white").pack(pady=10)
        tk.Label(self.root, text="Number of Screenshots:", bg="#2c3e50", fg="white").pack()
        self.screenshots_entry = tk.Entry(self.root)
        self.screenshots_entry.pack(pady=5)

        tk.Label(self.root, text="Interval (Seconds):", bg="#2c3e50", fg="white").pack()
        self.interval_entry = tk.Entry(self.root)
        self.interval_entry.pack(pady=5)

        tk.Label(self.root, text="Scene Name:", bg="#2c3e50", fg="white").pack()
        self.scene_entry = tk.Entry(self.root)
        self.scene_entry.pack(pady=5)

        tk.Label(self.root, text="Source Name:", bg="#2c3e50", fg="white").pack()
        self.source_entry = tk.Entry(self.root)
        self.source_entry.pack(pady=5)

        # Navigation buttons
        ttk.Button(self.root, text="Back", command=self.prev_page).pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Button(self.root, text="Next", command=self.save_screenshot_settings).pack(side=tk.RIGHT, padx=20, pady=10)

    def save_screenshot_settings(self):
        # Save screenshot settings
        self.config_data["screenshot"].update({
            "number_of_screens": int(self.screenshots_entry.get()),
            "interval_seconds": int(self.interval_entry.get()),
            "scene_name": self.scene_entry.get(),
            "source_name": self.source_entry.get()
        })
        self.next_page()

    def page_folders(self):
        self.clear_page()

        # Folder Selection Page
        tk.Label(self.root, text="Folder Settings", bg="#2c3e50", fg="white").pack(pady=10)
        
        # Screenshot Folder
        tk.Label(self.root, text="Screenshot Folder:", bg="#2c3e50", fg="white").pack()
        self.folder_button = ttk.Button(self.root, text="Browse...", command=self.select_folder)
        self.folder_button.pack(pady=5)
        self.folder_label = tk.Label(self.root, text="", bg="#2c3e50", fg="white")
        self.folder_label.pack()

        # Burst Folder
        tk.Label(self.root, text="Burst Folder:", bg="#2c3e50", fg="white").pack()
        self.folder_burst_button = ttk.Button(self.root, text="Browse...", command=self.select_burst_folder)
        self.folder_burst_button.pack(pady=5)
        self.folder_burst_label = tk.Label(self.root, text="", bg="#2c3e50", fg="white")
        self.folder_burst_label.pack()

        # Navigation buttons
        ttk.Button(self.root, text="Back", command=self.prev_page).pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Button(self.root, text="Finish", command=self.save_folders).pack(side=tk.RIGHT, padx=20, pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Screenshot Folder")
        if folder:
            self.config_data["screenshot"]["folder"] = folder
            self.folder_label.config(text=folder)

    def select_burst_folder(self):
        folder = filedialog.askdirectory(title="Select Burst Folder")
        if folder:
            self.config_data["screenshot"]["folder_burst"] = folder
            self.folder_burst_label.config(text=folder)

    def save_folders(self):
        self.config_data["screenshot"].update({
            "folder": self.config_data["screenshot"]["folder"],
            "folder_burst": self.config_data["screenshot"]["folder_burst"],
            "name": "screenshot"  # Default filename (or prompt user if needed)
        })
        self.save_config()

    def save_config(self):
        # Save the collected config data to config.toml
        with open(self.config_file_path, "w") as config_file:
            toml.dump(self.config_data, config_file)
        messagebox.showinfo("Success", "Configuration saved!")
        self.start_main_app()  # Close the config GUI and start the main application
class OBSController:
    def __init__(self):
        # Load configuration from config.toml
        self.config = self.load_config("config.toml")
        self.folder = self.config['screenshot']['folder']
        self.folder_burst = self.config['screenshot']['folder_burst']
        self.filename = self.config['screenshot']['name']
        self.number_of_screens = self.config['screenshot']['number_of_screens']  # Now an integer
        self.interval_seconds = self.config['screenshot']['interval_seconds']  # Now an integer
        self.CAMERA_IP = self.config["screenshot"]["ip"]
        self.BASE_URL = f"http://{self.CAMERA_IP}/cgi-bin/ptzctrl.cgi?ptzcmd&"
        self.server_port = self.config['screenshot']['OBS_WEBSOCKET_PORT']  # Now an integer
        self.server_password = self.config['screenshot']['WEBSOCKET_PASSWORD']

        # Load the scene and source name from config
        self.SCENE1 = self.config['screenshot']['scene_name']  # Loaded from config
        self.SourceName = self.config['screenshot']['source_name']  # Loaded from config

        # OBS WebSocket Client
        self.client = obs.ReqClient(host='localhost', port=self.server_port, password=self.server_password)

    # Method to load configuration from a TOML file
    def load_config(self, file_path):
        try:
            return toml.load(file_path)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    # Method to take a screenshot of a specified source


    def take_singleShot(self):
        # Generate a timestamp instead of random text
        date_now = datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g., "20231029_153045"
        # Construct the full file path with the timestamp
        image_file_path = os.path.join(self.folder, f"{self.filename}_{date_now}.png")
        
        try:
            # Use SaveSourceScreenshot to capture a screenshot
            response = self.client.save_source_screenshot(
                self.SourceName,
                "png",
                image_file_path,
                1920,
                1080,
                -1
            )
            print(f"Screenshot saved at: {image_file_path}, Response: {response}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")



    def divideBurst(self, random_text, index):
        image_file_path = os.path.join(self.folder_burst, f"{self.filename}_{random_text}{index}.png")  # Construct the full file path
        try:
            # Use SaveSourceScreenshot to capture a screenshot
            response = self.client.save_source_screenshot(
                self.SourceName,
                "png",
                image_file_path,
                1920,
                1080,
                -1
            )
            print(f"Screenshot saved at: {image_file_path}, Response: {response}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")

    # Method to take multiple screenshots in burst mode
    def take_burst_screenshots(self):
        date_now = datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g., "20231029_153045"
        for i in range(self.number_of_screens):
            self.divideBurst(date_now, i + 1)  # Use the same random text for all screenshots
            time.sleep(self.interval_seconds)  # Wait for the specified interval



    def send_command(self,command):
        url = f"{self.BASE_URL}{command}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text  # Assuming text response; change if JSON
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    # Function to send a command and stop afterward
    def send_command_with_stop(self,command, delay=0.5):

        """Send a command followed by a stop command after a delay."""
        print(f"Executing: {command}")
        self.send_command(command)
        time.sleep(delay)  # Delay before sending stop command
        print("Sending stop command")
        return self.send_command("stop")
    


        # Movement functions with auto-stop
    def move_left(self):
        return self.send_command_with_stop("posleft")

    def move_right(self):
        return self.send_command_with_stop("posright")

    def move_up(self):
        return self.send_command_with_stop("posup")

    def move_down(self):
        return self.send_command_with_stop("posdown")

    # Zoom functions with auto-stop
    def zoom_in(self):
        return self.send_command_with_stop("zoomtele")

    def zoom_out(self):
        return self.send_command_with_stop("zoomwide")

# Assuming OBSController class is already defined here or imported from another file

class OBSControllerGUI:
    def __init__(self, root, stop_event, config_gui_instance):
        self.root = root  # Store the root window as an attribute
        self.obs_controller = OBSController()  # Initialize the OBS controller instance
        self.stop_event = stop_event  # Event to signal stopping the main thread
        self.config_gui_instance = config_gui_instance  # Store reference to config GUI instance
        self.threads = []  # List to keep track of running threads

        # Set up the main window
        root.title("OBS Controller")
        root.geometry("300x500")  # Adjusted for new button space
        root.configure(bg="#2c3e50")  # Set background color for the window

        # Style configuration for buttons
        style = ttk.Style()
        style.configure("TButton",
                        background="#34495e",  # Dark button color
                        foreground="#2c3e50",  # Darker button text color
                        bordercolor="#1abc9c",  # Border color
                        borderwidth=2,  # Border width
                        relief="flat")  # Flat relief to remove default button look

        # Create Burst Mode and Snapshot buttons
        self.create_button_with_style(root, "Burst Mode", self.start_burst_mode_thread, 10)
        self.create_button_with_style(root, "Snapshot", self.take_snapshot_thread, 10)

        # Create a frame for directional buttons in a plus-sign layout
        direction_frame = tk.Frame(root, bg="#2c3e50")
        direction_frame.pack(pady=20)

        # Arrange directional buttons in a plus-sign configuration
        self.create_directional_buttons(direction_frame)

        # Zoom Buttons
        self.create_button_with_style(root, "Zoom In", self.zoom_in_thread, 5)
        self.create_button_with_style(root, "Zoom Out", self.zoom_out_thread, 5)

        # Learn More button
        self.create_button_with_style(root, "Learn More", self.open_learn_more, 10)

        # Set up close event handler
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle the window close event."""
        print("Closing the application.")
        self.stop_event.set()  # Signal to stop the threads

        # Optionally wait for threads to complete or clean up
        for thread in self.threads:
            thread.join(timeout=1)  # Wait for a maximum of 1 second

        try:
            if self.config_gui_instance and self.config_gui_instance.root.winfo_exists():
                self.config_gui_instance.root.destroy()  # Close the Config GUI
                self.config_gui_instance = None  # Clear the reference to prevent further access
        except Exception as e:
            # Handle the exception
            print(f"An error occurred while closing the Config GUI: {e}")


        self.root.quit()  # Close the Tkinter window


    def create_button_with_style(self, parent, text, command, padding):
        """Helper function to create a styled button with rounded corners."""
        button_frame = tk.Frame(parent, bg="#2c3e50", bd=0)
        button_frame.pack(pady=padding)

        # Create a canvas for rounded corners
        canvas = tk.Canvas(button_frame, width=250, height=40, bg="#2c3e50", highlightthickness=0)
        canvas.pack()

        # Draw rounded rectangle on the canvas
        r = 10  # Corner radius
        x0, y0, x1, y1 = 0, 0, 250, 40
        canvas.create_arc(x0, y0, x0 + 2 * r, y0 + 2 * r, start=90, extent=90, fill="#34495e", outline="#1abc9c", width=2)
        canvas.create_arc(x1 - 2 * r, y0, x1, y0 + 2 * r, start=0, extent=90, fill="#34495e", outline="#1abc9c", width=2)
        canvas.create_arc(x0, y1 - 2 * r, x0 + 2 * r, y1, start=180, extent=90, fill="#34495e", outline="#1abc9c", width=2)
        canvas.create_arc(x1 - 2 * r, y1 - 2 * r, x1, y1, start=270, extent=90, fill="#34495e", outline="#1abc9c", width=2)
        canvas.create_rectangle(x0 + r, y0, x1 - r, y1, fill="#34495e", outline="#1abc9c")
        canvas.create_rectangle(x0, y0 + r, x1, y1 - r, fill="#34495e", outline="#1abc9c")

        # Create button and place it on top of the canvas
        button = ttk.Button(button_frame, text=text, command=command, style="TButton")
        button.place(relx=0.5, rely=0.5, anchor='center')

    def create_directional_buttons(self, parent):
        """Helper function to create directional buttons in a plus-sign layout."""
        # Move Up Button
        move_up_button = ttk.Button(parent, text="Up", command=self.move_up_thread, style="TButton")
        move_up_button.grid(row=0, column=1, padx=5, pady=5)

        # Move Left Button
        move_left_button = ttk.Button(parent, text="Left", command=self.move_left_thread, style="TButton")
        move_left_button.grid(row=1, column=0, padx=5, pady=5)

        # Move Right Button
        move_right_button = ttk.Button(parent, text="Right", command=self.move_right_thread, style="TButton")
        move_right_button.grid(row=1, column=2, padx=5, pady=5)

        # Move Down Button
        move_down_button = ttk.Button(parent, text="Down", command=self.move_down_thread, style="TButton")
        move_down_button.grid(row=2, column=1, padx=5, pady=5)

    # Define functions for directional and other controls using threading
    def start_burst_mode_thread(self):
        thread = threading.Thread(target=self.obs_controller.take_burst_screenshots)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def take_snapshot_thread(self):
        thread = threading.Thread(target=self.obs_controller.take_singleShot)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def move_left_thread(self):
        thread = threading.Thread(target=self.obs_controller.move_left)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def move_right_thread(self):
        thread = threading.Thread(target=self.obs_controller.move_right)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def move_up_thread(self):
        thread = threading.Thread(target=self.obs_controller.move_up)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def move_down_thread(self):
        thread = threading.Thread(target=self.obs_controller.move_down)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def zoom_in_thread(self):
        thread = threading.Thread(target=self.obs_controller.zoom_in)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    def zoom_out_thread(self):
        thread = threading.Thread(target=self.obs_controller.zoom_out)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()
        self.threads.append(thread)  # Track the thread

    # Open URL method for Learn More button
    def open_learn_more(self):
        """Open the Learn More URL in a browser."""
        webbrowser.open("https://ptzoptics.com/CMP/")



def run_main_app(stop_event, config_gui_instance):
    """Function to create and run the main application GUI on the main thread."""
    root = tk.Tk()
    app = OBSControllerGUI(root, stop_event, config_gui_instance)  # Pass ConfigGUI instance
    root.mainloop()  # Start the Tkinter main loop

if __name__ == "__main__":
    # Event to signal stopping the main thread
    stop_event = threading.Event()

    # Run the Config GUI in the main thread
    config_root = tk.Tk()
    config_gui = ConfigGUI(config_root, stop_event)  # Pass stop_event here

    # Properly handle the close event to terminate the program
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            stop_event.set()  # Set the event to stop the main application
            config_root.destroy()  # Close the config GUI

    config_root.protocol("WM_DELETE_WINDOW", on_closing)  # Use the custom closing function
    config_root.mainloop()  # Block until the config GUI is closed

    # Run the main app after the config GUI is closed
    run_main_app(stop_event, config_gui)  # Pass the ConfigGUI instance to the main app