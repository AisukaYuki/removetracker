import requests
import sys

# qBittorrent Web UI 登录信息
qb_url = 'http://localhost:8080'
qb_username = 'admin'
qb_password = 'adminadmin'
target_tracker = 'test.com'

def login(session):
    login_url = f'{qb_url}/api/v2/auth/login'
    login_data = {
        'username': qb_username,
        'password': qb_password
    }
    print("尝试登录 qBittorrent Web UI...")
    response = session.post(login_url, data=login_data)
    response.raise_for_status()
    print("登录成功")

def get_torrent_trackers(session, torrent_hash):
    trackers_url = f'{qb_url}/api/v2/torrents/trackers?hash={torrent_hash}'
    response = session.get(trackers_url)
    response.raise_for_status()
    return response.json()

def remove_tracker(session, torrent_hash, tracker_url):
    remove_tracker_url = f'{qb_url}/api/v2/torrents/removeTrackers'
    remove_tracker_data = {
        'hash': torrent_hash,
        'urls': tracker_url
    }
    print(f"正在从种子 {torrent_hash} 删除 tracker {tracker_url}...")
    response = session.post(remove_tracker_url, data=remove_tracker_data)
    response.raise_for_status()
    print(f"成功从种子 {torrent_hash} 删除 tracker {tracker_url}")

def main(torrent_hash):
    try:
        session = requests.Session()
        # 登录 qBittorrent Web UI
        login(session)

        # 获取种子 trackers 信息
        trackers = get_torrent_trackers(session, torrent_hash)

        for tracker in trackers:
            tracker_url = tracker['url']
            if target_tracker in tracker_url:
                # 移除匹配的 tracker
                remove_tracker(session, torrent_hash, tracker_url)
                print(f'已移除种子 {torrent_hash} 中的 tracker: {tracker_url}')
                return  # 只需要移除第一个匹配的 tracker

        print("没有找到匹配的 tracker")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err.response.status_code} - {http_err.response.reason}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python remove_tracker.py <torrent_hash>")
        sys.exit(1)
    
    torrent_hash = sys.argv[1]
    main(torrent_hash)
