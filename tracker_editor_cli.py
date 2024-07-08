import requests
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def login(session, qb_url, qb_username, qb_password):
    login_url = f'{qb_url}/api/v2/auth/login'
    login_data = {
        'username': qb_username,
        'password': qb_password
    }
    logger.info("尝试登录 qBittorrent Web UI...")
    response = session.post(login_url, data=login_data)
    response.raise_for_status()
    logger.info("登录成功")

def search_torrents(session, qb_url, target_tracker):
    try:
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

def remove_tracker(session, qb_url):
    try:
        matched_torrents = getattr(search_torrents, 'matched_torrents', [])
        if not matched_torrents:
            logger.info("没有符合条件的种子，请先执行查找种子")
            return

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
            remove_response = session.post(remove_tracker_url, data=remove_tracker_data)
            remove_response.raise_for_status()
            logger.info(f"成功从种子 {torrent['name']} 删除 tracker {tracker_url}")

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

def replace_tracker(session, qb_url, target_tracker, new_tracker_part):
    try:
        matched_torrents = getattr(search_torrents, 'matched_torrents', [])
        if not matched_torrents:
            logger.info("没有符合条件的种子，请先执行查找种子")
            return

        for matched in matched_torrents:
            torrent = matched['torrent']
            tracker_url = matched['tracker_url']
            new_tracker_url = tracker_url.replace(target_tracker, new_tracker_part)

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
        
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

def main():
    qb_url = input("请输入qb地址，如 http://localhost:8080 : ")
    qb_username = input("输入用户名：")
    qb_password = input("输入密码：")

    session = requests.Session()
    login(session, qb_url, qb_username, qb_password)

    while True:
        print("请选择执行的操作：")
        print("1. 查找种子，输入tracker关键字")
        print("2. 移除tracker")
        print("3. 替换tracker字符串")
        choice = input("请输入选择的操作 (1/2/3) 或 'q' 退出: ")

        if choice == '1':
            target_tracker = input("请输入tracker关键字：")
            search_torrents(session, qb_url, target_tracker)
        elif choice == '2':
            remove_tracker(session, qb_url)
        elif choice == '3':
            target_tracker = input("请输入要替换的tracker字符串：")
            new_tracker_part = input("请输入新的字符串：")
            replace_tracker(session, qb_url, target_tracker, new_tracker_part)
        elif choice.lower() == 'q':
            break
        else:
            print("无效的选择，请重新输入。")

if __name__ == '__main__':
    main()
