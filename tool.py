import os
import sys
import threading
import time
from time import sleep
from datetime import datetime
import requests
import subprocess
from pystyle import Colors, Colorate, Write, Center, Box

# Ensure the current directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ANSI color codes
den = "\033[1;90m"
luc = "\033[1;32m"
trang = "\033[1;37m"
red = "\033[1;31m"
vang = "\033[1;33m"
tim = "\033[1;35m"
lamd = "\033[1;34m"
lam = "\033[1;36m"
purple = "\e[35m"
hong = "\033[1;95m"

thanh_xau = red + "[" + trang + "=.=" + red + "] " + trang + "=> "
thanh_dep = red + "[" + trang + "=.=" + red + "] " + trang + "=> "

# Lock for thread-safe printing
print_lock = threading.Lock()

# Thiết lập thư mục log
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'follow_client.log')

def log(message):
    """Ghi log vào console và file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with print_lock:
        print(f"{timestamp} - {message}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")

def get_device_id():
    """Lấy device_id của thiết bị Android"""
    try:
        result = subprocess.run(['getprop', 'ro.serialno'], capture_output=True, text=True, check=True)
        device_id = result.stdout.strip()
        log(f"Device ID: {device_id}")
        return device_id
    except Exception as e:
        log(f"Lỗi khi lấy device_id: {str(e)}")
        return None

def send_follow_request(url='http://10.0.0.2:8000/follow'):
    """Gửi yêu cầu Follow đến web server trên PC và nhận kết quả"""
    try:
        device_id = get_device_id()
        if not device_id:
            return "Error: Cannot get device_id"
        headers = {'Content-Type': 'application/json'}
        data = {'task': 'FOLLOW', 'device_id': device_id}
        log(f"Đang gửi yêu cầu đến {url} với device_id: {device_id}")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        log(f"Kết quả từ server: {result}")
        return result.get('result', 'Error: No result')
    except Exception as e:
        log(f"Lỗi khi gửi yêu cầu: {str(e)}")
        return f"Error: {str(e)}"

# Load devices from devices.txt
def load_devices(file_path="devices.txt"):
    devices = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 3:
                        index, username, token_tds = parts[0], parts[1], parts[2]
                        devices.append((index, username, token_tds))
                    else:
                        with print_lock:
                            print(red + f"[!] Dòng không hợp lệ trong {file_path}: {line}")
        if not devices:
            with print_lock:
                print(red + f"[!] File {file_path} rỗng hoặc không chứa thiết bị hợp lệ!")
            sys.exit(1)
        return devices
    except FileNotFoundError:
        with print_lock:
            print(red + f"[!] File {file_path} không tồn tại!")
        sys.exit(1)
    except Exception as e:
        with print_lock:
            print(red + f"[!] Lỗi khi đọc file {file_path}: {str(e)}")
        sys.exit(1)

# Open TikTok link using Termux
def open_tiktok_link(link):
    try:
        os.system(f'termux-open-url "{link}"')
        sleep(2)  # Wait for the link to open
        return True
    except Exception as e:
        with print_lock:
            print(red + f"[!] Không thể mở link TikTok: {str(e)}")
        return False

# Swipe down and press Back using Termux
def swipe_and_back():
    try:
        os.system("input keyevent KEYCODE_BACK")
        sleep(1)
        os.system("input swipe 500 1000 500 200 300")
    except Exception as e:
        with print_lock:
            print(red + f"[!] Lỗi khi vuốt hoặc nhấn Back: {str(e)}")

# Delay function
def delay(dl):
    try:
        for i in range(dl, -1, -1):
            with print_lock:
                print(f'{vang}[{trang}Mango{vang}][{trang}{i}{vang}]           ', end='\r')
            sleep(1)
    except:
        sleep(dl)
        with print_lock:
            print(' ', end='\r')

# TraoDoiSub_Api class
class TraoDoiSub_Api(object):
    def __init__(self, token):
        self.token = token
        self.headers = {
            'authority': 'traodoisub.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
            'user-agent': 'traodoisub tiktok tool',
        }
    
    def main(self):
        try:
            main = requests.get(f'https://traodoisub.com/api/?fields=profile&access_token={self.token}', headers=self.headers, timeout=5).json()
            try:
                return main['data']
            except:
                return False
        except:
            return False
    
    def run(self, user):
        try:
            run = requests.get(f'https://traodoisub.com/api/?fields=tiktok_run&id={user}&access_token={self.token}', headers=self.headers, timeout=5).json()
            try:
                return run['data']
            except:
                return False
        except:
            return False
    
    def get_job(self, type):
        try:
            get = requests.get(f'https://traodoisub.com/api/?fields={type}&access_token={self.token}', headers=self.headers, timeout=5)
            return get
        except:
            return False
    
    def cache(self, id, type):
        try:
            cache = requests.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}', headers=self.headers, timeout=5).json()
            try:
                cache['cache']
                return True
            except:
                return False
        except:
            return False

    def nhan_xu(self, id, type):
        try:
            nhan = requests.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}', headers=self.headers, timeout=5)
            try:
                xu = nhan.json()['data']['xu']
                msg = nhan.json()['data']['msg']
                job = nhan.json()['data']['job_success']
                xuthem = nhan.json()['data']['xu_them']
                with print_lock:
                    global total
                    total += xuthem
                    bongoc(14)
                    print(f'{lam}Nhận Thành Công {job} Nhiệm Vụ {red}| {luc}{msg} {red}| {luc}TOTAL {vang}{total} {luc}Xu {red}| {vang}{xu} ')
                    bongoc(14)
                if job == 0:
                    return 0
            except:
                if '"code":"error","msg"' in nhan.text:
                    hien = nhan.json()['msg']
                    with print_lock:
                        print(red + hien, end='\r')
                        sleep(2)
                        print(' ' * len(hien), end='\r')
                else:
                    with print_lock:
                        print(red + 'Nhận Xu Thất Bại !', end='\r')
                        sleep(2)
                        print(' ' * 50, end='\r')
                return False
        except:
            with print_lock:
                print(red + 'Nhận Xu Thất Bại !', end='\r')
                sleep(2)
                print(' ' * 50, end='\r')
            return False

# Separator line
def bongoc(so):
    for i in range(so):
        print(red + '────', end='')
    print('')

# Global variable for total coins
total = 0

# Process a single account
def process_account(index, username, token_tds, nhiem_vu, dl, nv_nhan):
    # Check token validity
    if not token_tds or token_tds.strip() == "":
        with print_lock:
            print(red + f"[!] Token TDS cho tài khoản {username} không hợp lệ!")
        return
    with print_lock:
        print(luc + f"[*] Đã đọc token TDS cho {username}: {token_tds[:10]}...")

    # Initialize TDS API with token
    tds = TraoDoiSub_Api(token_tds)
    data = tds.main()
    if not data:
        with print_lock:
            print(red + f"[!] Access Token Không Hợp Lệ cho tài khoản {username}! Vui lòng kiểm tra lại token trong devices.txt")
        return
    
    xu = data['xu']
    xudie = data['xudie']
    user = data['user']
    with print_lock:
        print(f'{lam}Đăng Nhập Thành Công - Tài khoản: {username}')
        print(f'{thanh_xau}{luc}Tên Tài Khoản: {vang}{user}')
        print(f'{thanh_xau}{luc}Xu Hiện Tại: {vang}{xu}')
        print(f'{thanh_xau}{luc}Xu Bị Phạt: {vang}{xudie}')
        bongoc(14)

    # Check TikTok account
    cau_hinh = tds.run(username)
    if cau_hinh != False:
        user = cau_hinh['uniqueID']
        id_acc = cau_hinh['id']
        with print_lock:
            bongoc(14)
            print(f'{luc}Đang Cấu Hình ID: {vang}{id_acc} {red}| {luc}User: {vang}{user} {red}|')
            bongoc(14)
    else:
        with print_lock:
            print(f'{red}Cấu Hình Thất Bại User: {vang}{username}')
        return

    dem = 0
    ntool = 0
    consecutive_nha_follow = 0  # Counter for consecutive "Nhả follow"
    max_consecutive_nha_follow = 5  # Max consecutive "Nhả follow
