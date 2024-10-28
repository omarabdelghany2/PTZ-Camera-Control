import obsws_python as obs
import os
import toml
import random
import string
import time

class OBSController:
    def __init__(self):
        # Load configuration from config.toml
        self.config = self.load_config("config.toml")
        self.folder = self.config['screenshot']['folder']
        self.filename = self.config['screenshot']['name']
        self.number_of_screens = self.config['screenshot']['number_of_screens']  # Add to your config
        self.interval_seconds = self.config['screenshot']['interval_seconds']  # Add to your config
        
        # OBS WebSocket Client
        self.SCENE1 = "SCENE1"
        self.SourceName = "Image"  # Example source name
        self.client = obs.ReqClient(host='localhost', port=4444, password='password')

    # Method to load configuration from a TOML file
    def load_config(self, file_path):
        try:
            return toml.load(file_path)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    # Method to generate random string of specified length
    def generate_random_string(self, length=4):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    # Method to take a screenshot of a specified source
    def take_screenshot(self, random_text, index):
        image_file_path = os.path.join(self.folder, f"{self.filename}_{random_text}{index}.png")  # Construct the full file path
        try:
            # Use SaveSourceScreenshot to capture a screenshot
            response = self.client.save_source_screenshot(
                self.SourceName,
                "png",
                image_file_path,
                None,
                None,
                -1
            )
            print(f"Screenshot saved at: {image_file_path}, Response: {response}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")

    # Method to take multiple screenshots in burst mode
    def take_burst_screenshots(self):
        random_text = self.generate_random_string()  # Generate random text once
        for i in range(self.number_of_screens):
            self.take_screenshot(random_text, i + 1)  # Use the same random text for all screenshots
            time.sleep(self.interval_seconds)  # Wait for the specified interval

# Instantiate and start the OBSController
if __name__ == "__main__":
    controller = OBSController()
    
    # Take burst screenshots
    controller.take_burst_screenshots()
