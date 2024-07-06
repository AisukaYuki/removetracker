import requests
import logging
import argparse

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def search_torrents(qb_url, qb_username, qb_password, target_tracker):
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

def remove_tracker(qb_url):
    try:
        matched_torrents = getattr(search_torrents, 'matched_torrents', [])
        if not matched_torrents:
            logger.info("没有符合条件的种子")
            return

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
            remove_response = session.post(remove_tracker_url, data=remove_tracker_data)
            remove_response.raise_for_status()
            logger.info(f"成功从种子 {torrent['name']} 删除 tracker {tracker_url}")

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

def replace_tracker(qb_url, target_tracker, new_tracker_part):
    try:
        matched_torrents = getattr(search_torrents, 'matched_torrents', [])
        if not matched_torrents:
            logger.info("没有符合条件的种子")
            return

        session = requests.Session()
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
    parser = argparse.ArgumentParser(description='qBittorrent Tracker Editor')
    subparsers = parser.add_subparsers(dest='command', required=True)

    search_parser = subparsers.add_parser('search', help='查找种子')
    search_parser.add_argument('-H', '--host', required=True, help='qBittorrent Web UI 的 URL，例如：http://localhost:8080')
    search_parser.add_argument('-u', '--username', required=True, help='qBittorrent Web UI 的用户名')
    search_parser.add_argument('-p', '--password', required=True, help='qBittorrent Web UI 的密码')
    search_parser.add_argument('-t', '--target-tracker', required=True, help='要查找的目标 Tracker 关键字')

    remove_parser = subparsers.add_parser('remove', help='删除 Tracker')
    remove_parser.add_argument('-H', '--host', required=True, help='qBittorrent Web UI 的 URL，例如：http://localhost:8080')
    remove_parser.add_argument('-u', '--username', required=True, help='qBittorrent Web UI 的用户名')
    remove_parser.add_argument('-p', '--password', required=True, help='qBittorrent Web UI 的密码')
    remove_parser.add_argument('-t', '--target-tracker', required=True, help='要删除的目标 Tracker 关键字')

    replace_parser = subparsers.add_parser('replace', help='替换 Tracker')
    replace_parser.add_argument('-H', '--host', required=True, help='qBittorrent Web UI 的 URL，例如：http://localhost:8080')
    replace_parser.add_argument('-u', '--username', required=True, help='qBittorrent Web UI 的用户名')
    replace_parser.add_argument('-p', '--password', required=True, help='qBittorrent Web UI 的密码')
    replace_parser.add_argument('-t', '--target-tracker', required=True, help='要查找的目标 Tracker 关键字，仅替换命中的字符串，请确保需要替换部分输入完整')
    replace_parser.add_argument('-n', '--new-tracker', required=True, help='用于替换的新的 Tracker 部分')

    args = parser.parse_args()

    if args.command == 'search':
        search_torrents(args.host, args.username, args.password, args.target_tracker)
    elif args.command == 'remove':
        remove_tracker(args.host, args.username, args.password, args.target_tracker)
    elif args.command == 'replace':
        replace_tracker(args.host, args.username, args.password, args.target_tracker, args.new_tracker)

if __name__ == '__main__':
    main()
