import numpy as np
import pyautogui as pg
import time 
import cv2
import mss
import threading

#Define frame time for auto clicker action
frametime = 1 / 120

class GuitarFlashAutoClicker:
    def __init__(self):

        # Mapping colors for their respective keys bindings 
        self.keys = {
            "green": "a",
            "red": "s",
            "yellow": "j",
            "blue": "k",
            "orange": "l"
        }

        # Define screen areas where each note may will appear
        # (might need ajustment depending on the monitor resolution)
        self.areas = {
            "green": (30, 0, 40, 40),
            "red": (120, 0, 40, 40),
            "yellow": (200, 0, 40, 40),
            "blue": (280, 0, 40, 40),
            "orange": (380, 0, 40, 40)
        }

        # Area to capture main game screen
        self.main_area = {"top": 920, "left": 500, "width": 450, "height": 30}

        # Lock to handle multi_threaded screenshot acess
        self.screenshot_lock = threading.Lock()
        self.screenshot = None

    def capture_screen(self):

        # Continuously capture the main game area to detect notes
        with mss.mss() as sct:
            while True:
                with self.screenshot_lock:
                    #Capture and stores screenshot as numpy array
                    self.screenshot = np.array(sct.grab(self.main_area))

                #Display main area screenshot for debuggin purposes  
                cv2.imshow("area", self.screenshot)

                #Exit condition (press 'q' to stop display) 
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()

    def detect_notes(self, color, area):

        # Detect notes for each color by analyzing the screenshot
        while True:
            with self.screenshot_lock: 

                # Skip if no screenshot is available
                if self.screenshot is None:
                    continue

            x, y, w, h = area
            note_region = self.screenshot[y : y + h, x : x + w]

            # Convert to grayscale and calculate mean intensity
            gray_frame = cv2.cvtColor(note_region, cv2.COLOR_BGR2GRAY)
            mean_intensity = np.mean(gray_frame)

            if mean_intensity > 65:
                pg.keyDown(self.keys[color]) # Key press simulation
                pg.keyUp(self.keys[color]) # Key release simulation

            # Sleep for frame time
            time.sleep(frametime)
                
    def start_game(self):
        # Start screen capture thread
        capture_thread = threading.Thread(target=self.capture_screen, daemon=True)
        capture_thread.start()

        threads = []

        # Start detection threads for each note color
        for color, area, in self.areas.items():
            thread = threading.Thread(target=self.detect_notes, args=(color, area))
            thread.start()
            threads.append(thread)

        # Keep the main thread alive to allow continuous gameplay
        while True:
            time.sleep(1)

if __name__ == "__main__":
    # Create and start the game automation
    guitar_flash = GuitarFlashAutoClicker()
    guitar_flash.start_game()   