import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 添加日志处理器来更新文本控件
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

def search_torrents():
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
        logger.info("尝试登录 qBittorrent Web UI...")
        response = session.post(login_url, data=login_data)
        response.raise_for_status()
        logger.info("登录成功")

        torrents_url = f'{qb_url}/api/v2/torrents/info'
        logger.info("获取种子信息...")
        response = session.get(torrents_url)
        response.raise_for_status()
        torrents = response.json()
        logger.info(f"找到 {len(torrents)} 个种子")

        matched_torrents = []
        for torrent in torrents:
            torrent_hash = torrent['hash']
            tracker_list_url = f'{qb_url}/api/v2/torrents/trackers?hash={torrent_hash}'
            response = session.get(tracker_list_url)
            response.raise_for_status()
            trackers = response.json()

            for tracker in trackers:
                if target_tracker in tracker['url']:
                    matched_torrents.append({
                        'torrent': torrent,
                        'tracker_url': tracker['url']
                    })
                    logger.info(f"种子 {torrent['name']} 符合条件，tracker: {tracker['url']}")

        if not matched_torrents:
            logger.info("没有符合条件的种子")
        else:
            logger.info(f"共有 {len(matched_torrents)} 个符合条件的种子")
            search_torrents.matched_torrents = matched_torrents
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        messagebox.showerror("错误", str(e))

def remove_tracker():
    try:
        matched_torrents = getattr(search_torrents, 'matched_torrents', [])
        if not matched_torrents:
            logger.info("没有符合条件的种子")
            return

        qb_url = qb_url_entry.get()

        session = requests.Session()
        for matched in matched_torrents:
            torrent = matched['torrent']
            tracker_url = matched['tracker_url']
            torrent_hash = torrent['hash']
            remove_tracker_url = f'{qb_url}/api/v2/torrents/removeTrackers'
            remove_tracker_data = {
                'hash': torrent_hash,
                'urls': tracker_url
            }
            logger.info(f"正在从种子 {torrent['name']} 删除 tracker {tracker_url}...")
            logger.debug(f"请求URL: {remove_tracker_url}")
            logger.debug(f"请求数据: {remove_tracker_data}")
            remove_response = session.post(remove_tracker_url, data=remove_tracker_data)
            remove_response.raise_for_status()
            logger.info(f"成功从种子 {torrent['name']} 删除 tracker {tracker_url}")

        messagebox.showinfo("成功", "完成tracker删除")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
        messagebox.showerror("HTTP错误", f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        messagebox.showerror("错误", str(e))

def replace_tracker():
    try:
        matched_torrents = getattr(search_torrents, 'matched_torrents', [])
        if not matched_torrents:
            logger.info("没有符合条件的种子")
            return
        qb_url = qb_url_entry.get()
        new_tracker_part = new_tracker_entry.get()  # 新tracker部分
        session = requests.Session()

        for matched in matched_torrents:
            torrent = matched['torrent']
            tracker_url = matched['tracker_url']
            new_tracker_url = tracker_url.replace(target_tracker_entry.get(), new_tracker_part)

            remove_tracker_url = f'{qb_url}/api/v2/torrents/removeTrackers'
            remove_tracker_data = {
                'hash': torrent['hash'],
                'urls': tracker_url
            }
            add_tracker_url = f'{qb_url}/api/v2/torrents/addTrackers'
            add_tracker_data = {
                'hash': torrent['hash'],
                'urls': new_tracker_url
            }

            # 先移除旧的tracker
            logger.info(f"正在从种子 {torrent['name']} 删除 tracker {tracker_url}...")
            remove_response = session.post(remove_tracker_url, data=remove_tracker_data)
            remove_response.raise_for_status()

            # 添加新的tracker
            logger.info(f"正在为种子 {torrent['name']} 添加新的 tracker {new_tracker_url}...")
            add_response = session.post(add_tracker_url, data=add_tracker_data)
            add_response.raise_for_status()

            logger.info(f"成功将种子 {torrent['name']} 的 tracker 从 {tracker_url} 修改为 {new_tracker_url}")
        
        messagebox.showinfo("成功", "完成tracker替换")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
        messagebox.showerror("HTTP错误", f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        messagebox.showerror("错误", str(e))

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 100
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
        
app = tk.Tk()
app.title("qBittorrent Tracker Editor")
app.resizable(False, False)

# 设置默认值
default_qb_url = 'http://localhost:8080'
default_qb_username = 'admin'
default_qb_password = 'adminadmin'
default_target_tracker = 'test'

tk.Label(app, text="qBittorrent URL", width=15, anchor="w").grid(row=0, column=0, sticky="w")
tk.Label(app, text="用户名", width=15, anchor="w").grid(row=1, column=0, sticky="w")
tk.Label(app, text="密码", width=15, anchor="w").grid(row=2, column=0, sticky="w")
tk.Label(app, text="目标Tracker", width=15, anchor="w").grid(row=3, column=0, sticky="w")
tk.Label(app, text="替换Tracker", width=15, anchor="w").grid(row=4, column=0, sticky="w")


qb_url_entry = tk.Entry(app, width=30)
qb_url_entry.insert(0, default_qb_url)

qb_username_entry = tk.Entry(app, width=30)
qb_username_entry.insert(0, default_qb_username)

qb_password_entry = tk.Entry(app, show='*', width=30)
qb_password_entry.insert(0, default_qb_password)

target_tracker_entry = tk.Entry(app, width=30)
target_tracker_entry.insert(0, default_target_tracker)


new_tracker_entry = tk.Entry(app, width=30)

qb_url_entry.grid(row=0, column=0, padx=(120, 0), pady=3, sticky="w")
qb_username_entry.grid(row=1, column=0, padx=(120, 0), pady=3, sticky="w")
qb_password_entry.grid(row=2, column=0, padx=(120, 0), pady=3, sticky="w")

target_tracker_entry.grid(row=3, column=0, padx=(120, 0), pady=3, sticky="w")
ToolTip(target_tracker_entry, "输出需要查找关键字，点击'查找种子'按钮，\n筛选需要操作的种子，以执行删除或替换。")

new_tracker_entry.grid(row=4, column=0, padx=(120, 0), pady=3, sticky="w")
ToolTip(new_tracker_entry, "注意，此功能仅替换'目标Tracker'一栏中命中的字符串。\n例如：'目标Tracker'一栏中填写test，'替换Tracker'填写baidu，则：\nhttps://www.test233.com/123456 会替换为  https://www.baidu233.com/123456")


button_frame = tk.Frame(app)
button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")

tk.Button(app, text="查找种子", command=search_torrents, width=10, cursor="hand2").grid(row=5, column=0, padx=(80, 0), pady=10, sticky="w")
tk.Button(app, text="删除Tracker", command=remove_tracker, width=10, cursor="hand2").grid(row=5, column=0, padx=(180, 0), pady=10, sticky="w")
tk.Button(app, text="替换Tracker", command=replace_tracker, width=10, cursor="hand2").grid(row=5, column=0, padx=(280, 0), pady=10, sticky="w")


# 添加日志输出窗口
log_text = scrolledtext.ScrolledText(app, height=15, state='disabled')
log_text.grid(row=6, columnspan=2, padx=3, pady=3, sticky="w")

# 配置日志处理器
text_handler = TextHandler(log_text)
text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(text_handler)

app.mainloop()