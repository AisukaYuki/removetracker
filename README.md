# removetracker
### 为什么会水这么一个东西。因为某站点双Tracker，连接其中一个另一个就报错，这让我很不爽。
qBittorrent Tracker Remover by ChatGPT-4o

更新了替换tracker功能。
### 打包成可执行文件
使用`pyinstaller`打包成可执行文件：

1. 安装`pyinstaller`（如果还未安装）：
   ```sh
   pip install pyinstaller
   ```

2. 使用`pyinstaller`打包脚本：
   ```sh
   pyinstaller --onefile --windowed tracker_editor.py
   ```

这样，你会得到一个包含默认值的GUI界面应用，并且可以将其打包成可执行文件用于分发和使用。

![image](https://github.com/AisukaYuki/removetracker/assets/17586327/4b629d5d-c944-4c05-8548-b7452e37c1c7)

**命令行版本使用示例**： cli脚本为交互式输入

### 新增脚本，在下载完成后自动执行移除操作

#### 配置 qBittorrent

1. 打开 qBittorrent。
2. 进入 “选项” -> “下载” -> “下载完成时运行外部程序”。
3. 勾选该选项并填写脚本路径和参数，例如：
   ```sh
   python /path/to/remove_tracker.py %I
   ```

#### 脚本执行流程

1. 脚本从命令行参数中获取种子的 info hash。
2. 脚本登录到 qBittorrent 的 Web UI。
3. 脚本获取指定种子的所有 tracker 信息。
4. 脚本检查每个 tracker，如果匹配到指定的 tracker URL，则调用 API 移除该 tracker。

通过这种方式，当种子完成下载时，qBittorrent 将运行该脚本，并传递种子的 info hash 给脚本。脚本将使用传递的 info hash 来检查并移除tracker。
