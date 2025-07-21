import os
import sys
import threading
from time import sleep
from datetime import datetime
import requests
from pystyle import Colors, Colorate, Write, Center, Box

# Ensure the current directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import follow_like.py functions
try:
    from follow_like import perform_action
except ImportError:
    print(Colors.red + "[!] Không tìm thấy follow_like.py trong cùng thư mục!")
    print(Colors.red + "[!] Vui lòng kiểm tra file follow_like.py tồn tại và đúng tên trong thư mục hiện tại.")
    sys.exit(1)

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
    max_consecutive_nha_follow = 5  # Max consecutive "Nhả follow" before stopping
    while True:
        if ntool == 2:
            break
        listfollow = tds.get_job('tiktok_follow')
        if listfollow == False:
            with print_lock:
                print(red + f'[{username}] Không Get Được Nhiệm Vụ Follow              ', end='\r')
                sleep(2)
                print(' ' * 50, end='\r')
        elif 'error' in listfollow.text:
            if listfollow.json()['error'] == 'Thao tác quá nhanh vui lòng chậm lại':
                coun = listfollow.json()['countdown']
                with print_lock:
                    print(f'{red}[{username}] Đang Get Nhiệm Vụ Follow, COUNTDOWN: {str(round(coun, 3))} ', end='\r')
                    sleep(2)
                    print(' ' * 50, end='\r')
            elif listfollow.json()["error"] == 'Vui lòng ấn NHẬN TẤT CẢ rồi sau đó tiếp tục làm nhiệm vụ để tránh lỗi!':
                tds.nhan_xu('TIKTOK_FOLLOW_API', 'TIKTOK_FOLLOW')
            else:
                with print_lock:
                    print(red + f'[{username}] {listfollow.json()["error"]}', end='\r')
                    sleep(2)
                    print(' ' * 50, end='\r')
        else:
            try:
                listfollow = listfollow.json()['data']
            except:
                with print_lock:
                    print(red + f'[{username}] Hết Nhiệm Vụ Follow                             ', end='\r')
                    sleep(2)
                    print(' ' * 50, end='\r')
                continue
            if len(listfollow) == 0:
                with print_lock:
                    print(red + f'[{username}] Hết Nhiệm Vụ Follow                             ', end='\r')
                    sleep(2)
                    print(' ' * 50, end='\r')
            else:
                with print_lock:
                    print(f'{luc}[{username}] Tìm Thấy {vang}{len(listfollow)} {luc}Nhiệm Vụ Follow                       ', end='\r')
                    sleep(2)
                    print(' ' * 50, end='\r')
                for i in listfollow:
                    id = i['id']
                    link = i['link']
                    if open_tiktok_link(link):
                        # Call perform_action from follow_like.py
                        result = perform_action("termux_device", 'follow')  # Placeholder device ID for Termux
                        if result == "Follow ok":
                            consecutive_nha_follow = 0  # Reset counter on success
                        elif result == "Nhả follow":
                            consecutive_nha_follow += 1
                            with print_lock:
                                print(red + f"[!] [{username}] Nhả follow cho ID: {id} (Lần {consecutive_nha_follow}/{max_consecutive_nha_follow})")
                            if consecutive_nha_follow >= max_consecutive_nha_follow:
                                with print_lock:
                                    print(red + f"[!] [{username}] Đã đạt {max_consecutive_nha_follow} lần Nhả follow liên tục. Dừng tool cho tài khoản {username}.")
                                return
                        else:
                            consecutive_nha_follow = 0  # Reset counter on other results

                        # Swipe down and press Back
                        swipe_and_back()
                        
                        cache = tds.cache(id, 'TIKTOK_FOLLOW_CACHE')
                        if cache != True:
                            tg = datetime.now().strftime('%H:%M:%S')
                            hien = f'{vang}[{red}X{vang}] {red}| {lam}{tg} {red}| {vang}FOLLOW {red}| {trang}{id} {red}|'
                            with print_lock:
                                print(hien, end='\r')
                                sleep(1)
                                print(' ' * 80, end='\r')
                        else:
                            dem += 1
                            tg = datetime.now().strftime('%H:%M:%S')
                            with print_lock:
                                print(f'{vang}[{trang}{dem}{vang}] {red}| {lam}{tg} {red}| {Colorate.Horizontal(Colors.yellow_to_red, "FOLLOW")} {red}| {trang}{id} {red}|')
                            delay(dl)
                            if dem % nv_nhan == 0:
                                nhan = tds.nhan_xu('TIKTOK_FOLLOW_API', 'TIKTOK_FOLLOW')
                                if nhan == 0:
                                    with print_lock:
                                        print(luc + f'[{username}] Nhận Xu Thất Bại Acc Tiktok Của Bạn Ổn Chứ ')
                                        print(f'{thanh_xau}{luc}Nhập {red}[{vang}1{red}] {luc}Để Thay Nhiệm Vụ ')
                                        print(f'{thanh_xau}{luc}Nhập {red}[{vang}2{red}] {luc}Thay Acc Tiktok ')
                                        print(f'{thanh_xau}{luc}Nhấn {red}[{vang}Enter{red}] {luc}Để Tiếp Tục')
                                    chon = input(f'{thanh_xau}{luc}Nhập {trang}===>: {vang}')
                                    if chon == '1':
                                        ntool = 2
                                        break
                                    elif chon == '2':
                                        ntool = 1
                                        break
                                    with print_lock:
                                        bongoc(14)
        if ntool == 1 or ntool == 2:
            break

# Main function
def main():
    os.system('clear')
    banner = '''
    ████████╗██████╗ ███████╗
    ╚══██╔══╝██╔══██╗██╔════╝
       ██║   ██║  ██║███████╗
       ██║   ██║  ██║╚════██║
       ██║   ██████╔╝███████║
       ╚═╝   ╚═════╝ ╚══════╝
    '''
    print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(banner)))
    print(red + Center.XCenter(Box.DoubleCube("Tool TDS TikTok Multi-Task v1.7 - Termux")))

    # Verify follow_like.py exists
    if not os.path.isfile("follow_like.py"):
        print(Colors.red + "[!] File follow_like.py không tồn tại trong thư mục hiện tại!")
        print(Colors.red + "[!] Vui lòng đảm bảo follow_like.py được đặt cùng thư mục với tool.py.")
        sys.exit(1)

    # Load devices from devices.txt
    device_list = load_devices()
    if not device_list:
        print(red + "[!] Không tìm thấy tài khoản nào trong devices.txt!")
        sys.exit(1)

    # Auto-select Follow task, Delay=6, Claim coins after 8 jobs
    nhiem_vu = '2'
    dl = 6
    nv_nhan = 8

    # Create threads for each account
    threads = []
    for index, username, token_tds in device_list:
        thread = threading.Thread(target=process_account, args=(index, username, token_tds, nhiem_vu, dl, nv_nhan))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(luc + "[*] Đã xử lý tất cả tài khoản. Thoát chương trình.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(red + "\n[!] Đã thoát chương trình.")
        sys.exit(0)
