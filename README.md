# removetracker
qBittorrent Tracker Remover by ChatGPT-4o

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


PS:为什么会水这么一个东西。因为某PT站点双Tracker，连接其中一个，另一个就报错。这让我很不爽。
