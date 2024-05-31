# removetracker
qBittorrent Tracker Remover by ChatGPT-4o

### 完整Python脚本
```python
import tkinter as tk
from tkinter import messagebox
import requests

def remove_tracker():
    qb_url = qb_url_entry.get()
    qb_username = qb_username_entry.get()
    qb_password = qb_password_entry.get()
    target_tracker = target_tracker_entry.get()

    if not qb_url or not qb_username or not qb_password or not target_tracker:
        messagebox.showwarning("输入错误", "请填写所有字段")
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

        messagebox.showinfo("成功", "完成tracker删除")
    except Exception as e:
        messagebox.showerror("错误", str(e))

app = tk.Tk()
app.title("qBittorrent Tracker Remover")

# 设置默认值
default_qb_url = 'http://localhost:8080'
default_qb_username = 'admin'
default_qb_password = ''
default_target_tracker = 'tracker.cinefiles.info'

tk.Label(app, text="qBittorrent URL").grid(row=0)
tk.Label(app, text="用户名").grid(row=1)
tk.Label(app, text="密码").grid(row=2)
tk.Label(app, text="目标Tracker").grid(row=3)

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

tk.Button(app, text="删除Tracker", command=remove_tracker).grid(row=4, columnspan=2, pady=10)

app.mainloop()
```

### 解释
1. **设置默认值**：在定义输入框时，使用`insert`方法插入默认值。例如：
   ```python
   qb_url_entry.insert(0, default_qb_url)
   ```
2. **默认值变量**：定义默认值变量，方便修改和管理：
   ```python
   default_qb_url = 'http://localhost:8080'
   default_qb_username = 'admin'
   default_qb_password = ''
   default_target_tracker = 'tracker.cinefiles.info'
   ```
3. **保持现有功能**：除了添加默认值，其他功能保持不变，包括登录qBittorrent、获取种子信息、查找并删除特定tracker的逻辑。

### 打包成可执行文件
按照前述步骤使用`pyinstaller`打包成可执行文件：

1. 安装`pyinstaller`（如果还未安装）：
   ```sh
   pip install pyinstaller
   ```

2. 使用`pyinstaller`打包脚本：
   ```sh
   pyinstaller --onefile --windowed your_script_name.py
   ```

这样，你会得到一个包含默认值的GUI界面应用，并且可以将其打包成可执行文件用于分发和使用。
