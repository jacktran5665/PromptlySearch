#!/usr/bin/env python3
import tkinter as tk
import threading
import webbrowser
import urllib.parse
import keyboard
import pystray
from PIL import Image, ImageDraw
import sys
import re


class SearchHotKeyApp:
    def __init__(self):
        self.popup_window = None
        self.tray_icon = None
        self.running = True
        
    def create_tray_image(self):
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([15, 15, 35, 35], outline='#0078D4', width=4)
        draw.line([32, 32, 45, 45], fill='#0078D4', width=4)
        return image

    def create_search_popup(self):
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.lift()
            self.popup_window.focus_force()
            return
            
        self.popup_window = tk.Toplevel()
        self.popup_window.overrideredirect(True)
        self.popup_window.configure(bg='#2D2D30')
        self.popup_window.attributes('-topmost', True)
        self.center_window(self.popup_window, 500, 60)
        
        frame = tk.Frame(self.popup_window, bg='#1E1E1E')
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        content = tk.Frame(frame, bg='#1E1E1E')
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(content, text="🔍", font=("Arial", 16), bg='#1E1E1E', fg='#FFFFFF').pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(content, font=("Segoe UI", 14), bg='#1E1E1E', fg='#888888',
                                   bd=0, insertbackground='#FFFFFF', selectbackground='#0078D4')
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Type to search...")
        
        self.search_entry.bind('<FocusIn>', lambda e: self.clear_placeholder())
        self.search_entry.bind('<FocusOut>', lambda e: self.restore_placeholder())
        self.search_entry.bind('<Return>', self.perform_search)
        self.popup_window.bind('<Escape>', lambda e: self.close_popup())
        
        self.search_entry.focus_force()
        self.search_entry.select_range(0, tk.END)

    def center_window(self, window, width, height):
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def clear_placeholder(self):
        if self.search_entry.get() == "Type to search...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg='#FFFFFF')

    def restore_placeholder(self):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Type to search...")
            self.search_entry.configure(fg='#888888')

    def perform_search(self, event=None):
        query = self.search_entry.get().strip()
        if query and query != "Type to search...":
            webbrowser.open(self.get_url(query))
        self.close_popup()

    def get_url(self, query):
        if query.startswith(('http://', 'https://')):
            return query
        
        if ('.' in query and 
            (re.match(r'^[\w\-]+\.[\w\-]+', query) or 
             query.startswith('localhost') or 
             re.match(r'^\d+\.\d+\.\d+\.\d+', query))):
            return f"https://{query}"
        
        return f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"

    def close_popup(self):
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
        self.popup_window = None

    def on_hotkey(self):
        if self.running:
            threading.Thread(target=self.show_popup, daemon=True).start()

    def show_popup(self):
        if not hasattr(self, 'root'):
            self.root = tk.Tk()
            self.root.withdraw()
        self.root.after(0, self.create_search_popup)

    def quit_app(self, icon=None, item=None):
        self.running = False
        try:
            keyboard.unhook_all()
        except:
            pass
        
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
        
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.quit()
            self.root.destroy()
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        sys.exit(0)

    def run(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        try:
            keyboard.add_hotkey('ctrl+space', self.on_hotkey)
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return
        
        menu = pystray.Menu(pystray.MenuItem("Quit", self.quit_app))
        self.tray_icon = pystray.Icon("SearchHotKey", self.create_tray_image(), menu=menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        
        print("Search HotKey started. Press Ctrl+Space to search.")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()


def main():
    if getattr(sys, 'frozen', False):
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    try:
        SearchHotKeyApp().run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()