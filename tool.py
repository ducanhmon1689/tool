import os
import sys
import threading
from time import sleep
from datetime import datetime
from ppadb.client import Client as AdbClient
import requests
from pystyle import Colors, Colorate, Write, Center, Box

# Import follow_like.py functions
try:
    from follow_like import perform_action
except ImportError:
    print(Colors.red + "[!] Không tìm thấy follow_like.py trong cùng thư mục!")
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

# Initialize ADB and list devices
def init_adb():
    try:
        adb = AdbClient(host="127.0.0.1", port=5037)
        devices = adb.devices()
        if not devices:
            with print_lock:
                print(red + "[!] Không có thiết bị ADB nào được kết nối. Vui lòng kết nối ít nhất một thiết bị với chế độ gỡ lỗi USB.")
            return None
        return devices
    except Exception as e:
        with print_lock:
            print(red + f"[!] Khởi tạo ADB thất thất bại: {str(e)}")
        return None

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
                        index, udid, username, token_tds = parts[0], parts[1], parts[2], parts[3]
                        devices.append((index, udid, username, token_tds))
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

# Select ADB device that matches UDID from devices.txt
def select_device(devices, udid):
    for device in devices:
        if device.serial == udid:
            try:
                model = device.shell("getprop ro.product.model").strip()
                with print_lock:
                    print(luc + f"[*] Đã chọn thiết bị: {model} (Serial: {device.serial})")
                return device
            except:
                with print_lock:
                    print(luc + f"[*] Đã chọn thiết bị: (Serial: {device.serial})")
                return device
    with print_lock:
        print(red + f"[!] Thiết bị với UDID {udid} không được kết nối qua ADB!")
    return None

# Push TikTok link to selected device via ADB
def open_tiktok_link(device, link):
    try:
        command = f'am start -a android.intent.action.VIEW -d "{link}"'
        device.shell(command)
        return True
    except Exception as e:
        with print_lock:
            print(red + f"[!] Không thể mở link TikTok: {str(e)}")
        return False

# Swipe down and press Back using ADB
def swipe_and_back(device):
    try:
        # Press Back
        device.shell("input keyevent KEYCODE_BACK")
        sleep(1)
        # Swipe down
        device.shell("input swipe 500 1000 500 200 300")
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
    
    def main(self):
        try:
            main = requests.get(f'https://traodoisub.com/api/?fields=profile&access_token={self.token}').json()
            try:
                return main['data']
            except:
                return False
        except:
            return False
    
    def run(self, user):
        try:
            run = requests.get(f'https://traodoisub.com/api/?fields=tiktok_run&id={user}&access_token={self.token}').json()
            try:
                return run['data']
            except:
                return False
        except:
            return False
    
    def get_job(self, type):
        try:
            get = requests.get(f'https://traodoisub.com/api/?fields={type}&access_token={self.token}')
            return get
        except:
            return False
    
    def cache(self, id, type):
        try:
            cache = requests.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}').json()
            try:
                cache['cache']
                return True
            except:
                return False
        except:
            return False

    def nhan_xu(self, id, type):
        try:
            nhan = requests.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}')
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

# Process a single device
def process_device(udid, username, token_tds, devices, nhiem_vu, dl, nv_nhan):
    # Check token validity
    if not token_tds or token_tds.strip() == "":
        with print_lock:
            print(red + f"[!] Token TDS cho tài khoản {username} không hợp lệ!")
        return
    with print_lock:
        print(luc + f"[*] Đã đọc token TDS cho {username}: {token_tds[:10]}...")

    # Initialize TDS API with token from devices.txt
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

    # Select ADB device
    device = select_device(devices, udid)
    if not device:
        with print_lock:
            print(red + f"[!] Bỏ qua thiết bị {udid} vì không kết nối được.")
        return

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
                    print(' mayankita2025', end='\r')
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
                    if open_tiktok_link(device, link):
                        # Wait 2 seconds to ensure the link is opened
                        sleep(2)
                        # Call perform_action from follow_like.py
                        result = perform_action(device.serial, 'follow')
                        if result == "Follow ok":
                            consecutive_nha_follow = 0  # Reset counter on success
                        elif result == "Nhả follow":
                            consecutive_nha_follow += 1
                            with print_lock:
                                print(red + f"[!] [{username}] Nhả follow cho ID: {id} (Lần {consecutive_nha_follow}/{max_consecutive_nha_follow})")
                            if consecutive_nha_follow >= max_consecutive_nha_follow:
                                with print_lock:
                                    print(red + f"[!] [{username}] Đã đạt {max_consecutive_nha_follow} lần Nhả follow liên tục. Dừng tool cho thiết bị {udid}.")
                                return
                        else:
                            consecutive_nha_follow = 0  # Reset counter on failure

                        # Swipe down and press Back
                        swipe_and_back(device)
                        
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
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = '''
    ████████╗██████╗ ███████╗
    ╚══██╔══╝██╔══██╗██╔════╝
       ██║   ██║  ██║███████╗
       ██║   ██║  ██║╚════██║
       ██║   ██████╔╝███████║
       ╚═╝   ╚═════╝ ╚══════╝
    '''
    print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(banner)))
    print(red + Center.XCenter(Box.DoubleCube("Tool TDS TikTok Multi-Task v1.7 - Multi-Device")))

    # Initialize ADB
    devices = init_adb()
    if not devices:
        print(red + "[!] Thoát chương trình do không có thiết bị ADB.")
        sys.exit(1)

    # Load devices from devices.txt
    device_list = load_devices()
    if not device_list:
        print(red + "[!] Không tìm thấy thiết bị nào trong devices.txt!")
        sys.exit(1)

    # Auto-select Follow task, Delay=10, Claim coins after 8 jobs
    nhiem_vu = '2'
    dl = 6
    nv_nhan = 8

    # Create threads for each device
    threads = []
    for _, udid, username, token_tds in device_list:
        thread = threading.Thread(target=process_device, args=(udid, username, token_tds, devices, nhiem_vu, dl, nv_nhan))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(luc + "[*] Đã xử lý tất cả thiết bị. Thoát chương trình.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(red + "\n[!] Đã thoát chương trình.")
        sys.exit(0)
