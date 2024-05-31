import tkinter as tk
from tkinter import messagebox
import requests

def remove_tracker():
    qb_url = qb_url_entry.get()
    qb_username = qb_username_entry.get()
    qb_password = qb_password_entry.get()
    target_tracker = target_tracker_entry.get()

    if not qb_url or not qb_username or not qb_password or not target_tracker:
        messagebox.showwarning("Input error", "Please fill in all fields")
        return

    try:
        session = requests.Session()
        login_url = f'{qb_url}/api/v2/auth/login'
        login_data = {
            'username': qb_username,
            'password': qb_password
        }
        response = session.post(login_url, data=login_data)
        response.raise_for_status()

        torrents_url = f'{qb_url}/api/v2/torrents/info'
        response = session.get(torrents_url)
        response.raise_for_status()
        torrents = response.json()

        for torrent in torrents:
            torrent_hash = torrent['hash']
            tracker_list_url = f'{qb_url}/api/v2/torrents/trackers?hash={torrent_hash}'
            response = session.get(tracker_list_url)
            response.raise_for_status()
            trackers = response.json()

            for tracker in trackers:
                if target_tracker in tracker['url']:
                    remove_tracker_url = f'{qb_url}/api/v2/torrents/removeTrackers'
                    remove_tracker_data = {
                        'hash': torrent_hash,
                        'urls': tracker['url']
                    }
                    remove_response = session.post(remove_tracker_url, data=remove_tracker_data)
                    remove_response.raise_for_status()
                    print(f"Removed tracker {tracker['url']} from torrent {torrent['name']}")

        messagebox.showinfo("Successful", "Tracker Removed")
    except Exception as e:
        messagebox.showerror("Error", str(e))

app = tk.Tk()
app.title("qBittorrent Tracker Remover")

# 设置默认值
default_qb_url = 'http://localhost:8080'
default_qb_username = 'admin'
default_qb_password = 'adminadmin'
default_target_tracker = 'test.com'

tk.Label(app, text="qBittorrent URL").grid(row=0)
tk.Label(app, text="username").grid(row=1)
tk.Label(app, text="password").grid(row=2)
tk.Label(app, text="Tracker").grid(row=3)

qb_url_entry = tk.Entry(app, width=50)
qb_url_entry.insert(0, default_qb_url)

qb_username_entry = tk.Entry(app, width=50)
qb_username_entry.insert(0, default_qb_username)

qb_password_entry = tk.Entry(app, show='*', width=50)
qb_password_entry.insert(0, default_qb_password)

target_tracker_entry = tk.Entry(app, width=50)
target_tracker_entry.insert(0, default_target_tracker)

qb_url_entry.grid(row=0, column=1, pady=5)
qb_username_entry.grid(row=1, column=1, pady=5)
qb_password_entry.grid(row=2, column=1, pady=5)
target_tracker_entry.grid(row=3, column=1, pady=5)

tk.Button(app, text="Remove", command=remove_tracker).grid(row=4, columnspan=2, pady=10)

app.mainloop()