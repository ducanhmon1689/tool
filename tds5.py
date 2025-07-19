# Coded by Traodoisub.com
import os
from time import sleep
from datetime import datetime
import subprocess

os.environ['TZ'] = 'Asia/Ho_Chi_Minh'

try:
    import requests
except:
    os.system("pip3 install requests")
    import requests

try:
    from pystyle import Colors, Colorate, Write, Center, Add, Box
except:
    os.system("pip3 install pystyle")
    from pystyle import Colors, Colorate, Write, Center, Add, Box

headers = {
    'authority': 'traodoisub.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'user-agent': 'traodoisub tiktok tool',
}

def login_tds(token):
    try:
        r = requests.get('https://traodoisub.com/api/?fields=profile&access_token='+token, headers=headers, timeout=5).json()
        if 'success' in r:
            os.system('clear')
            print(Colors.green + f"Đăng nhập thành công!\nUser: {Colors.yellow + r['data']['user'] + Colors.green} | Xu hiện tại: {Colors.yellow + r['data']['xu']}")
            return 'success'
        else:
            print(Colors.red + f"Token TDS không hợp lệ, hãy kiểm tra lại!\n")
            return 'error_token'
    except:
        return 'error'

def load_job(type_job, token):
    try:
        r = requests.get(f'https://traodoisub.com/api/?fields={type_job}&access_token={token}', headers=headers, timeout=5).json()
        if 'data' in r:
            return r
        elif "countdown" in r:
            sleep(round(r['countdown']))
            print(Colors.red + f"{r['error']}\n")
            return 'error_countdown'
        else:
            print(Colors.red + f"{r['error']}\n")
            return 'error_error'
    except:
        return 'error'

def duyet_job(type_job, token, uid):
    try:
        r = requests.get(f'https://traodoisub.com/api/coin/?type={type_job}&id={uid}&access_token={token}', headers=headers, timeout=5).json()
        if "cache" in r:
            return r['cache']
        elif "success" in r:
            dai = f'{Colors.yellow}------------------------------------------'
            print(dai)
            print(f"{Colors.cyan}Nhận thành công {r['data']['job_success']} nhiệm vụ | {Colors.green}{r['data']['msg']} | {Colors.yellow}{r['data']['xu']}")
            print(dai)
            return 'error'
        else:
            print(f"{Colors.red}{r['error']}")
            return 'error'
    except:
        return 'error'

def check_tiktok(id_tiktok, token):
    try:
        r = requests.get(f'https://traodoisub.com/api/?fields=tiktok_run&id={id_tiktok}&access_token={token}', headers=headers, timeout=5).json()
        if 'success' in r:
            os.system('clear')
            print(Colors.green + f"{r['data']['msg']}|ID: {Colors.yellow + r['data']['id'] + Colors.green}")
            return 'success'
        else:
            print(Colors.red + f"{r['error']}\n")
            return 'error_token'
    except:
        return 'error'

os.system('clear')
banner = r'''
████████╗██████╗ ███████╗
╚══██╔══╝██╔══██╗██╔════╝
   ██║   ██║  ██║███████╗
   ██║   ██║  ██║╚════██║
   ██║   ██████╔╝███████║
   ╚═╝   ╚═════╝ ╚══════╝
'''
gach = '========================================='
option = f'''{gach}{Colors.green}
Danh sách nhiệm vụ tool hỗ trợ: {Colors.red}
1. Follow
2. Tym
3. Follow + Tym
{Colors.yellow}{gach}
'''
option_acc = f'''{gach}{Colors.green}
Danh sách lựa chọn: {Colors.red}
1. Tiếp tục sử dụng acc TDS đã lưu
2. Sử dụng acc TDS mới
{Colors.yellow}{gach}
'''
print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(banner)))
print(Colors.red + Center.XCenter(Box.DoubleCube("Tool TDS tiktok free version 1.1")))

while True:
    try:
        f = open('TDS.txt', 'r')
        token_tds = f.read()
        f.close()
        cache = 'old'
    except FileNotFoundError:
        token_tds = Write.Input("Nhập token TDS:", Colors.green_to_yellow, interval=0.0025)
        cache = 'new'

    for _ in range(3):
        check_log = login_tds(token_tds)
        if check_log == 'success' or check_log == 'error_token':
            break
        else:
            sleep(2)

    if check_log == 'success':
        if cache == 'old':
            while True:
                print(option_acc)
                try:
                    choice = int(Write.Input("Lựa chọn của bạn là (Ví dụ: sử dụng acc cũ nhập 1):", Colors.green_to_yellow, interval=0.0025))
                    if choice in [1, 2]:
                        break
                    else:
                        os.system('clear')
                        print(Colors.red + f"Lỗi lựa chọn!! Chỉ nhập 1 hoặc 2\n")
                except:
                    os.system('clear')
                    print(Colors.red + f"Lỗi lựa chọn!! Chỉ nhập 1 hoặc 2\n")

            os.system('clear')
            if choice == 1:
                break
            else:
                os.remove('TDS.txt')
        else:
            f = open('TDS.txt', 'w')
            f.write(f'{token_tds}')
            f.close()
            break
    else:
        sleep(1)
        os.system('clear')

if check_log == 'success':
    # Nhập user tiktok
    while True:
        id_tiktok = Write.Input("Nhập ID tiktok chạy (lấy ở mục cấu hình web):", Colors.green_to_yellow, interval=0.0025)
        for _ in range(3):
            check_log = check_tiktok(id_tiktok, token_tds)
            if check_log == 'success' or check_log == 'error_token':
                break
            else:
                sleep(2)

        if check_log == 'success':
            break
        elif check_log == 'error_token':
            os.system('clear')
            print(Colors.red + f"ID tiktok chưa được thêm vào cấu hình, vui lòng thêm vào cấu hình rồi nhập lại!\n")
        else:
            os.system('clear')
            print(Colors.red + f"Lỗi sever vui lòng nhập lại!\n")

    # Lựa chọn nhiệm vụ
    while True:
        print(option)
        try:
            choice = int(Write.Input("Lựa chọn nhiệm vụ muốn làm (Ví dụ: Follow nhập 1):", Colors.green_to_yellow, interval=0.0025))
            if choice in [1, 2, 3]:
                break
            else:
                os.system('clear')
                print(Colors.red + f"Lỗi lựa chọn!! Chỉ nhập 1, 2 hoặc 3\n")
        except:
            os.system('clear')
            print(Colors.red + f"Lỗi lựa chọn!! Chỉ nhập 1, 2 hoặc 3\n")

    # Nhập delay nhiệm vụ
    while True:
        try:
            delay = int(Write.Input("Thời gian delay giữa các job (giây):", Colors.green_to_yellow, interval=0.0025))
            if delay > 2:
                break
            else:
                os.system('clear')
                print(Colors.red + f"Delay tối thiểu là 3\n")
        except:
            os.system('clear')
            print(Colors.red + f"Vui lòng nhập một số > 2\n")

    # Nhập max nhiệm vụ
    while True:
        try:
            max_job = int(Write.Input("Dừng lại khi làm được số nhiệm vụ là:", Colors.green_to_yellow, interval=0.0025))
            if max_job > 9:
                break
            else:
                os.system('clear')
                print(Colors.red + f"Tối thiểu là 10\n")
        except:
            os.system('clear')
            print(Colors.red + f"Vui lòng nhập một số > 9\n")

    os.system('clear')

    if choice == 1:
        type_load = 'tiktok_follow'
        type_duyet = 'TIKTOK_FOLLOW_CACHE'
        type_nhan = 'TIKTOK_FOLLOW'
        type_type = 'FOLLOW'
    elif choice == 2:
        type_load = 'tiktok_like'
        type_duyet = 'TIKTOK_LIKE_CACHE'
        type_nhan = 'TIKTOK_LIKE'
        type_type = 'TYM'
    else:  # choice == 3
        type_load = ['tiktok_follow', 'tiktok_like']
        type_duyet = ['TIKTOK_FOLLOW_CACHE', 'TIKTOK_LIKE_CACHE']
        type_nhan = ['TIKTOK_FOLLOW', 'TIKTOK_LIKE']
        type_type = 'FOLLOW+TYM'

    dem_tong = 0
    dem_duyet = 0  # Biến đếm số job để nhận xu

    while True:
        if choice == 3:
            # Luân phiên thực hiện Follow và Tym
            for i, load_type in enumerate(type_load):
                list_job = load_job(load_type, token_tds)
                sleep(2)
                if isinstance(list_job, dict):
                    for job in list_job['data']:
                        uid = job['id']
                        link = job['link']
                        os.system(f'termux-open-url {link}')
                        sleep(3)
                        os.system(f"input tap 540 650")
                        sleep(2)
                        check_duyet = duyet_job(type_duyet[i], token_tds, uid)
                        if check_duyet != 'error':
                            dem_tong += 1
                            dem_duyet += 1
                            t_now = datetime.now().strftime("%H:%M:%S")
                            print(f'{Colors.yellow}[{dem_tong}] {Colors.red}| {Colors.cyan}{t_now} {Colors.red}| {Colors.pink}{type_type} {Colors.red}| {Colors.light_gray}{uid}')
                            if dem_duyet == 10:  # Nhận xu sau 10 job
                                sleep(3)
                                duyet_job(type_nhan[i], token_tds, uid)
                                dem_duyet = 0  # Reset đếm sau khi nhận xu
                        if type_load[i] == 'tiktok_follow':  # Thực hiện back cho Follow hoặc Follow+Tym
                            for j in range(2):
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] {Colors.cyan}🔙 Thực hiện hành động Back lần {j+1}")
                                subprocess.run(['input', 'keyevent', 'KEYCODE_BACK'])
                                sleep(5)
                        if dem_tong == max_job:
                            break
                        else:
                            for j in range(delay, -1, -1):
                                print(Colors.green + 'Vui lòng đợi: ' + str(j) + ' giây', end='\r')
                                sleep(1)
                    if dem_tong == max_job:
                        break
        else:
            list_job = load_job(type_load, token_tds)
            sleep(2)
            if isinstance(list_job, dict):
                for job in list_job['data']:
                    uid = job['id']
                    link = job['link']
                    os.system(f'termux-open-url {link}')
                    sleep(3)
                    os.system(f"input tap 540 650")
                    sleep(2)
                    check_duyet = duyet_job(type_duyet, token_tds, uid)
                    if check_duyet != 'error':
                        dem_tong += 1
                        dem_duyet += 1
                        t_now = datetime.now().strftime("%H:%M:%S")
                        print(f'{Colors.yellow}[{dem_tong}] {Colors.red}| {Colors.cyan}{t_now} {Colors.red}| {Colors.pink}{type_type} {Colors.red}| {Colors.light_gray}{uid}')
                        if dem_duyet == 5:  # Nhận xu sau 5 job
                            sleep(3)
                            duyet_job(type_nhan, token_tds, uid)
                            dem_duyet = 0  # Reset đếm sau khi nhận xu
                    
                    if dem_tong == max_job:
                        break
                    else:
                        for j in range(delay, -1, -1):
                            print(Colors.green + 'Vui lòng đợi: ' + str(j) + ' giây', end='\r')
                            sleep(1)

        if dem_tong == max_job:
            # Nhận xu lần cuối nếu còn job chưa nhận
            if dem_duyet > 0:
                sleep(3)
                if choice == 3:
                    duyet_job(type_nhan[i], token_tds, uid)
                else:
                    duyet_job(type_nhan, token_tds, uid)
            print(f'{Colors.green}Hoàn thành {max_job} nhiệm vụ!')
            break
