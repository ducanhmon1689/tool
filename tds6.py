import os
import sys
import threading
import requests
from time import sleep
from datetime import datetime
from pystyle import Colors, Colorate, Write, System
from sys import platform

# Import follow_like.py functions
try:
    from follow_like import send_follow_request
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

# Global variable for total coins
total = 0
may = 'mb' if platform[0:3] == 'lin' else 'pc'

def banner():
    os.system("clear")
    banner_text = """
    ████████╗██████╗ ███████╗
    ╚══██╔══╝██╔══██╗██╔════╝
       ██║   ██║  ██║███████╗
       ██║   ██║  ██║╚════██║
       ██║   ██████╔╝███████║
       ╚═╝   ╚═════╝ ╚══════╝
    """
    print(Colorate.Horizontal(Colors.yellow_to_red, banner_text))

def bongoc(so):
    with print_lock:
        for i in range(so):
            print(red + '────', end='')
        print('')

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

def chuyen(link, may):
    if may == 'mb':
        os.system(f'termux-open-url {link}')
    else:
        os.system(f'cmd /c start {link}')

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

def process_device(username, token_tds, nhiem_vu, dl, nv_nhan):
    if not token_tds or token_tds.strip() == "":
        with print_lock:
            print(red + f"[!] Token TDS cho tài khoản {username} không hợp lệ!")
        return
    
    with print_lock:
        print(luc + f"[*] Đã đọc token TDS cho {username}: {token_tds[:10]}...")

    tds = TraoDoiSub_Api(token_tds)
    data = tds.main()
    if not data:
        with print_lock:
            print(red + f"[!] Access Token Không Hợp Lệ cho tài khoản {username}! Vui lòng kiểm tra lại token trong configtds.txt")
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
    consecutive_nha_follow = 0
    max_consecutive_nha_follow = 5
    while True:
        if ntool == 2:
            break
        if '2' in nhiem_vu:
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
                        print(f'{red}[{username}] Thử lại sau {vang}{str(round(coun, 3))} {red}giây', end='\r')
                    delay(coun)  # Chờ hết thời gian countdown
                    with print_lock:
                        print(' ' * 50, end='\r')
                    continue  # Tiếp tục vòng lặp sau khi chờ
                elif listfollow.json()['error'] == 'Vui lòng ấn NHẬN TẤT CẢ rồi sau đó tiếp tục làm nhiệm vụ để tránh lỗi!':
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
                        chuyen(link, may)
                        sleep(2)
                        result = send_follow_request()
                        if result == "Follow ok":
                            consecutive_nha_follow = 0
                        elif result == "Nhả follow":
                            consecutive_nha_follow += 1
                            with print_lock:
                                print(red + f"[!] [{username}] Nhả follow cho ID: {id} (Lần {consecutive_nha_follow}/{max_consecutive_nha_follow})")
                            if consecutive_nha_follow >= max_consecutive_nha_follow:
                                with print_lock:
                                    print(red + f"[!] [{username}] Đã đạt {max_consecutive_nha_follow} lần Nhả follow liên tục. Dừng tool cho tài khoản {username}.")
                                return
                        else:
                            consecutive_nha_follow = 0
                        
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

def main():
    banner()
    devices = []
    try:
        with open('configtds.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        username, token_tds = parts[0], parts[1]
                        devices.append((username, token_tds))
                    else:
                        with print_lock:
                            print(red + f"[!] Dòng không hợp lệ trong configtds.txt: {line}")
        if not devices:
            with print_lock:
                print(red + "[!] File configtds.txt rỗng hoặc không chứa thiết bị hợp lệ!")
            sys.exit(1)
    except FileNotFoundError:
        token = input(f'{thanh_xau}{luc}Nhập Access_Token TDS: {vang}')
        username = input(f'{thanh_xau}{luc}Nhập User Name Tik Tok: {vang}')
        with open('configtds.txt', 'w') as f:
            f.write(f"{username}\t{token}")
        devices = [(username, token)]

    nhiem_vu = '2'  # Auto-select Follow task
    dl = 6          # Delay 6 seconds
    nv_nhan = 8     # Claim coins after 8 jobs

    threads = []
    for username, token_tds in devices:
        thread = threading.Thread(target=process_device, args=(username, token_tds, nhiem_vu, dl, nv_nhan))
        threads.append(thread)
        thread.start()

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
