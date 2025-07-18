# Coded by Traodoisub.com, modified for Termux on Android
import os
import sys
import random
from time import sleep
from datetime import datetime
try:
    import cloudscraper
except ImportError:
    os.system("pip install cloudscraper")
    import cloudscraper
from pystyle import Colors, Colorate, Write, Center, Box
import subprocess

# Import follow_like.py functions
try:
    from follow_like import perform_action, log
except ImportError:
    print(Colors.red + "❌ Không tìm thấy follow_like.py trong cùng thư mục!")
    sys.exit(1)

# Rotating user-agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
]

# Load devices from devices.txt
def load_devices(file_path="devices.txt"):
    devices = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        index, udid, username, tiktok_id = parts[0], parts[1], parts[2], parts[3]
                        if not tiktok_id.isdigit():
                            print(Colors.red + f"[!] tiktok_id không hợp lệ (phải là số): {line}")
                            continue
                        devices.append((index, udid, username, tiktok_id))
                    else:
                        print(Colors.red + f"[!] Dòng không hợp lệ trong {file_path}: {line}")
                        continue
            if not devices:
                print(Colors.red + f"[!] File {file_path} rỗng hoặc không chứa thiết bị hợp lệ!")
                sys.exit(1)
        return devices
    except FileNotFoundError:
        print(Colors.red + f"[!] File {file_path} không tồn tại!")
        sys.exit(1)
    except Exception as e:
        print(Colors.red + f"[!] Lỗi khi đọc file {file_path}: {str(e)}")
        sys.exit(1)

# Select username from devices.txt
def select_username(devices):
    print(Colors.yellow + "\nDanh sách tài khoản TikTok:")
    for i, (_, _, username, _) in enumerate(devices, 1):
        print(f"{Colors.green}[{i}] {username}")
    while True:
        try:
            choice = int(input(Colors.cyan + "Nhập số thứ tự tài khoản: "))
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            print(Colors.red + f"Vui lòng chọn số từ 1 đến {len(devices)}!")
        except ValueError:
            print(Colors.red + "Vui lòng nhập số hợp lệ!")

# Check TikTok account ID
def check_tiktok(id_tiktok, token, tiktok_id):
    scraper = cloudscraper.create_scraper()
    retry_attempts = 3
    retry_delay = 5
    for attempt in range(retry_attempts):
        headers['user-agent'] = random.choice(USER_AGENTS)
        try:
            url = f"https://traodoisub.com/api/?fields=tiktok_run&id={tiktok_id}&access_token={token}"
            r = scraper.get(url, headers=headers, timeout=10).json()
            log(f"Phản hồi API tiktok_run: {r}")
            
            if 'success' in r:
                if r['data']['unique_username'] == id_tiktok:
                    log(f"Tài khoản TikTok hợp lệ: {id_tiktok} | ID: {r['data']['id']}")
                    return 'success'
                else:
                    log(f"Username không khớp: API trả về {r['data']['unique_username']}, mong đợi {id_tiktok}")
                    return 'error_token'
            else:
                error_msg = r.get('error', 'Không rõ nguyên nhân')
                log(f"Lỗi khi kiểm tra TikTok ID: {error_msg}")
                if "xác minh bạn không phải robot" in error_msg.lower():
                    log("Vui lòng xác minh CAPTCHA thủ công trên traodoisub.com!")
                if attempt < retry_attempts - 1:
                    wait_time = retry_delay + random.uniform(2, 5)
                    log(f"Thử lại sau {wait_time:.1f} giây...")
                    sleep(wait_time)
                    retry_delay *= 2
                continue
        except Exception as e:
            log(f"Lỗi kết nối khi kiểm tra TikTok ID: {str(e)}")
            if attempt < retry_attempts - 1:
                wait_time = retry_delay + random.uniform(2, 5)
                log(f"Thử lại sau {wait_time:.1f} giây...")
                sleep(wait_time)
                retry_delay *= 2
            continue
    log(f"Đã thử {retry_attempts} lần, không thể kiểm tra TikTok ID.")
    return 'error'

# Login to TDS
def login_tds(token):
    scraper = cloudscraper.create_scraper()
    retry_attempts = 3
    retry_delay = 5
    for attempt in range(retry_attempts):
        headers['user-agent'] = random.choice(USER_AGENTS)
        try:
            r = scraper.get(
                f'https://traodoisub.com/api/?fields=profile&access_token={token}',
                headers=headers,
                timeout=10
            ).json()
            if 'success' in r:
                log(f"Đăng nhập thành công! User: {r['data']['user']} | Xu hiện tại: {r['data']['xu']}")
                return 'success'
            else:
                log(f"Token TDS không hợp lệ: {r.get('error', 'Không rõ nguyên nhân')}")
                return 'error_token'
        except Exception as e:
            log(f"Lỗi kết nối khi đăng nhập TDS: {str(e)}")
            if attempt < retry_attempts - 1:
                wait_time = retry_delay + random.uniform(2, 5)
                log(f"Thử lại sau {wait_time:.1f} giây...")
                sleep(wait_time)
                retry_delay *= 2
            continue
    return 'error'

# Load job from TDS
def load_job(type_job, token):
    scraper = cloudscraper.create_scraper()
    retry_attempts = 3
    retry_delay = 5
    for attempt in range(retry_attempts):
        headers['user-agent'] = random.choice(USER_AGENTS)
        try:
            r = scraper.get(
                f'https://traodoisub.com/api/?fields={type_job}&access_token={token}',
                headers=headers,
                timeout=10
            ).json()
            if 'data' in r:
                return r
            elif "countdown" in r:
                wait_time = round(r['countdown'])
                log(f"Chờ {wait_time} giây do giới hạn API (lần thử {attempt+1}/{retry_attempts})...")
                sleep(wait_time + random.uniform(0, 2))
                retry_delay *= 2
                continue
            else:
                log(f"Lỗi khi lấy job: {r.get('error', 'Không rõ nguyên nhân')}")
                return 'error_error'
        except Exception as e:
            log(f"Lỗi kết nối khi lấy job: {str(e)}")
            if attempt < retry_attempts - 1:
                wait_time = retry_delay + random.uniform(2, 5)
                log(f"Thử lại sau {wait_time:.1f} giây...")
                sleep(wait_time)
                retry_delay *= 2
            continue
    log(f"Đã thử {retry_attempts} lần, không thể lấy job.")
    return 'error'

# Confirm job completion
def duyet_job(type_job, token, uid):
    scraper = cloudscraper.create_scraper()
    headers['user-agent'] = random.choice(USER_AGENTS)
    try:
        r = scraper.get(
            f'https://traodoisub.com/api/coin/?type={type_job}&id={uid}&access_token={token}',
            headers=headers,
            timeout=10
        ).json()
        if "cache" in r:
            return r['cache']
        elif "success" in r:
            log(f"Nhận thành công {r['data']['job_success']} nhiệm vụ | {r['data']['msg']} | {r['data']['xu']} xu")
            return 'success'
        else:
            log(f"Lỗi khi xác minh job: {r.get('error', 'Không rõ nguyên nhân')}")
            return 'error'
    except Exception as e:
        log(f"Lỗi kết nối khi xác minh job: {str(e)}")
        return 'error'


# Open TikTok link using Termux
def open_tiktok_link(link):
    try:
        subprocess.run(['termux-open-url', link], check=True)
        log(f"Đã mở link TikTok: {link}")
        return True
    except Exception as e:
        log(f"Không thể mở link TikTok: {str(e)}")
        return False

# Headers for TDS API
headers = {
    'authority': 'traodoisub.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'user-agent': random.choice(USER_AGENTS),
}

# Main function
def main():
    os.system('clear')
    banner = r'''
████████╗██████╗ ███████╗
╚══██╔══╝██╔══██╗██╔════╝
   ██║   ██║  ██║███████╗
   ██║   ██║  ██║╚════██║
   ██║   ██████╔╝███████║
   ╚═╝   ╚═════╝ ╚══════╝
'''
    print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(banner)))
    print(Colors.red + Center.XCenter(Box.DoubleCube("Tool TDS TikTok Termux v1.0")))

    # Load token
    try:
        with open('TDS.txt', 'r', encoding='utf-8') as f:
            token_tds = f.read().strip()
            if not token_tds:
                print(Colors.red + "[!] File TDS.txt rỗng! Vui lòng thêm token hợp lệ.")
                sys.exit(1)
        log(f"[*] Đã đọc token từ TDS.txt: {token_tds[:10]}...")
    except FileNotFoundError:
        print(Colors.red + "[!] Vui lòng thêm token TDS vào file TDS.txt!")
        sys.exit(1)

    # Load devices and select username
    devices = load_devices()
    index, udid, username, tiktok_id = select_username(devices)
    log(f"Bắt đầu làm việc với tài khoản {username} (ID: {tiktok_id})")

    # Login to TDS
    for _ in range(3):
        check_log = login_tds(token_tds)
        if check_log == 'success' or check_log == 'error_token':
            break
        sleep(2 + random.uniform(0, 2))

    if check_log != 'success':
        log(f"Bỏ qua do lỗi đăng nhập TDS.")
        sys.exit(1)

    # Check TikTok account
    for _ in range(3):
        check_log = check_tiktok(username, token_tds, tiktok_id)
        if check_log == 'success' or check_log == 'error_token':
            break
        sleep(2 + random.uniform(0, 2))

    if check_log != 'success':
        log(f"Bỏ qua do lỗi kiểm tra TikTok ID.")
        sys.exit(1)

    # Configuration
    task_delay = 20  # Delay after opening link
    job_delay = 20   # Delay between jobs
    max_jobs = 100   # Maximum jobs
    task_choice = 3  # 1: Follow, 2: Like, 3: Follow + Like

    # Configure job types
    job_types = []
    task_actions = []
    if task_choice == 1:
        job_types = [('tiktok_follow', 'TIKTOK_FOLLOW_CACHE', 'TIKTOK_FOLLOW', 'FOLLOW', 'TIKTOK_FOLLOW_API')]
        task_actions = ['follow']
    elif task_choice == 2:
        job_types = [('tiktok_like', 'TIKTOK_LIKE_CACHE', 'TIKTOK_LIKE', 'TYM', 'TIKTOK_LIKE_API')]
        task_actions = ['like']
    else:
        job_types = [
            ('tiktok_follow', 'TIKTOK_FOLLOW_CACHE', 'TIKTOK_FOLLOW', 'FOLLOW', 'TIKTOK_FOLLOW_API'),
            ('tiktok_like', 'TIKTOK_LIKE_CACHE', 'TIKTOK_LIKE', 'TYM', 'TIKTOK_LIKE_API')
        ]
        task_actions = ['follow', 'like']

    # Run jobs
    dem_tong = 0
    jobs_completed = 0
    while dem_tong < max_jobs:
        for type_load, type_duyet, type_nhan, type_type, api_type in job_types:
            list_job = load_job(type_load, token_tds)
            sleep(2 + random.uniform(0, 2))
            if isinstance(list_job, dict) and 'data' in list_job:
                for job in list_job['data']:
                    uid = job['id']
                    link = job['link']

                    # Open link
                    if open_tiktok_link(link):
                        log(f"Đang chờ 5 giây trước khi thực hiện nhiệm vụ...")
                        sleep(5)

                        # Perform tasks
                        for action in task_actions:
                            log(f"Đang thực hiện {action} cho link: {link}")
                            success = perform_action(None, action)  # None vì không dùng ADB
                            if success:
                                log(f"Hoàn thành {action} thành công!")
                            else:
                                log(f"Không thể hoàn thành {action}.")
                            sleep(2 + random.uniform(0, 1))

                        # Wait for remaining task delay
                        remaining_delay = task_delay - 5
                        if remaining_delay > 0:
                            log(f"Đang chờ {remaining_delay} giây để hoàn thành nhiệm vụ...")
                            sleep(remaining_delay)

                        # Confirm job
                        check_duyet = duyet_job(type_duyet, token_tds, uid)

                        if check_duyet != 'error':
                            dem_tong += 1
                            jobs_completed += 1
                            t_now = datetime.now().strftime("%H:%M:%S")
                            print(f'{Colors.yellow}[{dem_tong}] {Colors.red}| {Colors.cyan}{t_now} {Colors.red}| {Colors.pink}{type_type} {Colors.red}| {Colors.light_gray}{uid} | {Colors.green}{link}')

                            # Claim coins
                            if jobs_completed >= 5 or check_duyet > 9:
                                sleep(3 + random.uniform(0, 2))
                                result = duyet_job(type_nhan, token_tds, api_type)
                                if result == 'success':
                                    log(f"Đã nhận xu thành công!")
                                    jobs_completed = 0

                        # Delay between jobs
                        for i in range(job_delay, -1, -1):
                            print(Colors.green + f'Vui lòng đợi: {i} giây', end='\r')
                            sleep(1)

                    if dem_tong >= max_jobs:
                        break

                if dem_tong >= max_jobs:
                    log(f"Hoàn thành {max_jobs} nhiệm vụ!")
                    break
            else:
                log(f"Không thể tải danh sách nhiệm vụ. Đang thử lại...")
                sleep(5 + random.uniform(0, 2))

        if dem_tong >= max_jobs:
            break

    log(f"Đã hoàn thành công việc cho tài khoản {username}.")
    print(Colors.green + "[*] Thoát chương trình.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Colors.red + "\n[!] Đã thoát chương trình.")
        sys.exit(0)
