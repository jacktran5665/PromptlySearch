import pystray
from PIL import Image, ImageDraw
import subprocess
import sys
import os
import threading
import time
import ctypes


class PromptlyTrayApp:
    """System tray application that manages the search hotkey process. Provides tray icon 
    controls and automatic process monitoring with restart capabilities."""
    
    def __init__(self):
        self.search_process = None
        self.tray_icon = None
        self.running = True
        
        if getattr(sys, 'frozen', False) or sys.platform == 'win32':
            try:
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            except:
                pass

    def create_tray_image(self):
        """Creates a magnifying glass icon for the system tray."""
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([15, 15, 35, 35], outline='#0078D4', width=4)
        draw.line([32, 32, 45, 45], fill='#0078D4', width=4)
        return image

    def start_search_app(self, icon=None, item=None):
        """Starts or restarts the search hotkey application subprocess."""
        if self.search_process and self.search_process.poll() is None:
            return
            
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            search_script = os.path.join(script_dir, 'search_hotkey.py')
            
            self.search_process = subprocess.Popen(
                [sys.executable, search_script],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            threading.Thread(target=self.monitor_search_process, daemon=True).start()
            
        except Exception as e:
            print(f"Failed to start search application: {e}")

    def monitor_search_process(self):
        """Monitors the search process and automatically restarts it if it crashes."""
        while self.running and self.search_process:
            if self.search_process.poll() is not None:
                if self.running:
                    time.sleep(1)
                    if self.running:
                        self.start_search_app()
                break
            time.sleep(1)

    def stop_search_app(self):
        """Stops the search hotkey application subprocess."""
        if self.search_process and self.search_process.poll() is None:
            try:
                self.search_process.terminate()
                try:
                    self.search_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.search_process.kill()
            except Exception as e:
                print(f"Error stopping search application: {e}")
        self.search_process = None

    def show_about(self, icon=None, item=None):
        pass

    def quit_app(self, icon=None, item=None):
        """Quits the entire application and stops all processes."""
        self.running = False
        self.stop_search_app()
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        sys.exit(0)

    def run(self):
        """Runs the system tray application with menu and automatic search app startup."""
        menu = pystray.Menu(
            pystray.MenuItem("Start Search App", self.start_search_app, default=True),
            pystray.MenuItem("About", self.show_about, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "Promptly",
            self.create_tray_image(),
            "Promptly - Press Ctrl+Space to search",
            menu=menu
        )
        
        self.start_search_app()
        
        try:
            self.tray_icon.run()
        except KeyboardInterrupt:
            self.quit_app()


def main():
    try:
        PromptlyTrayApp().run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()