import obsws_python as obs
import os
import toml
import random
import string

class OBSController:
    def __init__(self):
        # Load configuration from config.toml
        self.config = self.load_config("config.toml")
        self.folder = self.config['screenshot']['folder']
        self.filename = self.config['screenshot']['name']

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
    def take_screenshot(self):
        random_text = self.generate_random_string()  # Generate random text
        # Construct the full file path with random text
        image_file_path = os.path.join(self.folder, f"{self.filename}_{random_text}.png")
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

# Instantiate and start the OBSController
if __name__ == "__main__":
    controller = OBSController()
    
    # Take a screenshot
    controller.take_screenshot()
