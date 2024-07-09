import tkinter as tk
from tkinter import ttk
from ytmusicapi import YTMusic
import yt_dlp
import threading
import time

class MusicDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Music Downloader")
        self.master.geometry("600x400")

        self.ytmusic = YTMusic()

        self.search_frame = ttk.Frame(self.master)
        self.search_frame.pack(pady=10)

        self.search_entry = ttk.Entry(self.search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_music)
        self.search_button.pack(side=tk.LEFT)

        self.result_frame = ttk.Frame(self.master)
        self.result_frame.pack(pady=10, expand=True, fill=tk.BOTH)

        self.result_tree = ttk.Treeview(self.result_frame, columns=("Title", "Artist"), show="headings")
        self.result_tree.heading("Title", text="Title")
        self.result_tree.heading("Artist", text="Artist")
        self.result_tree.pack(expand=True, fill=tk.BOTH)

        self.download_button = ttk.Button(self.master, text="Download", command=self.download_music)
        self.download_button.pack(pady=10)

        self.status_label = ttk.Label(self.master, text="")
        self.status_label.pack(pady=5)

    def search_music(self):
        query = self.search_entry.get()
        search_results = self.ytmusic.search(query, filter="songs")

        self.result_tree.delete(*self.result_tree.get_children())

        for result in search_results:
            title = result['title']
            # Handle cases where artist info is missing
            artist = result['artists'][0]['name'] if result.get('artists') else "Unknown Artist"
            video_id = result['videoId']
            self.result_tree.insert("", "end", values=(title, artist), tags=(video_id,))

        # Add a delay after search
        time.sleep(1)

    def download_music(self):
        selected_item = self.result_tree.selection()
        if not selected_item:
            self.status_label.config(text="Please select a song to download")
            return

        video_id = self.result_tree.item(selected_item)['tags'][0]
        url = f"https://www.youtube.com/watch?v={video_id}"

        self.status_label.config(text="Downloading...")
        threading.Thread(target=self.download_thread, args=(url,)).start()

    def download_thread(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.master.after(0, lambda: self.status_label.config(text="Download complete!"))
        except Exception as e:
            self.master.after(0, lambda: self.status_label.config(text=f"Download failed: {str(e)}"))

        # Add a delay after download
        time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicDownloaderApp(root)
    root.mainloop()