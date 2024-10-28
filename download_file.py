import os
import requests
from urllib.parse import urlparse
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

def center_window(window, width=400, height=200):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.resizable(False, False)  # Fixed window size

def get_filename_from_url(url):
    """Extracts the filename from the URL."""
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)

def paste_clipboard(event):
    """Paste clipboard content into the URL entry when clicked."""
    try:
        clipboard_content = root.clipboard_get()
        url_entry.delete(0, tk.END)
        url_entry.insert(0, clipboard_content)
    except tk.TclError:
        # If clipboard is empty or has an incompatible format, do nothing
        pass

def download_file():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a URL.")
        return

    # Get the filename
    filename = get_filename_from_url(url)
    save_path = filedialog.asksaveasfilename(initialfile=filename, defaultextension=".bin",
                                             filetypes=[("All files", "*.*"), ("ZIP files", "*.zip"), ("JPEG files", "*.jpg"), ("PNG files", "*.png")])
    if not save_path:
        return  # If no path is selected, cancel the download

    # Start download in a separate thread
    threading.Thread(target=download_and_save, args=(url, save_path)).start()

def download_and_save(url, save_path):
    try:
        # Make the request and get the total size
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        # Initialize progress bar
        progress_bar['value'] = 0
        progress_bar['maximum'] = total_size
        downloaded = 0
        
        # Download with progress display
        with open(save_path, "wb") as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                downloaded += len(data)
                progress_bar['value'] = downloaded  # Update the progress bar
                root.update_idletasks()
        
        messagebox.showinfo("Success", f"Download completed: {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download the file.\n{str(e)}")

# GUI setup
root = tk.Tk()
root.title("File Downloader")
center_window(root, width=400, height=200)

tk.Label(root, text="Enter URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)
url_entry.bind("<Button-1>", paste_clipboard)  # Paste clipboard content on click

progress_bar = ttk.Progressbar(root, length=350)
progress_bar.pack(pady=10)

download_button = tk.Button(root, text="Download", command=download_file)
download_button.pack(pady=20)

root.mainloop()
