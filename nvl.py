import os
import time
import json

# Kiểm tra và cài đặt thư viện requests
try:
    import requests
except ImportError:
    print("Đang cài đặt thư viện requests...")
    os.system("pip install requests")
    import requests

# Kiểm tra và cài đặt thư viện pystyle
try:
    from pystyle import Colors, Colorate, Write, Center, Box
except ImportError:
    print("Đang cài đặt thư viện pystyle...")
    os.system("pip install pystyle")
    from pystyle import Colors, Colorate, Write, Center, Box

from datetime import datetime

# Color functions
def error_color(string: str):
    return Colors.red + str(string) + Colors.reset
def success_color(string: str):
    return Colors.green + str(string) + Colors.reset
def system_color(string: str):
    return Colors.yellow + str(string) + Colors.reset
def info_color(string: str):
    return Colors.cyan + str(string) + Colors.reset

# GoLike API headers
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://app.golike.net/account/manager/tiktok',
}

# Load or save GoLike credentials
def load_credentials():
    try:
        with open('Authorization.txt', 'r') as f_auth, open('token.txt', 'r') as f_t:
            auth = f_auth.read().strip()
            t = f_t.read().strip()
            if auth and t:
                return auth, t
            else:
                raise FileNotFoundError
    except FileNotFoundError:
        auth = Write.Input("Nhập Authorization token của GoLike: ", Colors.green_to_yellow, interval=0.0025)
        t = Write.Input("Nhập t token của GoLike: ", Colors.green_to_yellow, interval=0.0025)
        with open('Authorization.txt', 'w') as f_auth, open('token.txt', 'w') as f_t:
            f_auth.write(auth)
            f_t.write(t)
        return auth, t

# Check TikTok account
def check_tiktok_account(auth, t):
    headers['Authorization'] = auth
    headers['t'] = t
    try:
        response = requests.get('https://gateway.golike.net/api/tiktok-account', headers=headers, json={}, timeout=5)
        data = response.json()
        if data.get('status') == 200 and data.get('success'):
            accounts = [(account['id'], account.get('nickname', account.get('unique_username', 'N/A'))) for account in data['data']]
            print(success_color(f"Đã tìm thấy {len(accounts)} tài khoản TikTok được liên kết!"))
            for i, (acc_id, username) in enumerate(accounts, 1):
                print(info_color(f"{i}. {username} (ID: {acc_id})"))
            return accounts
        else:
            print(error_color(f"Lỗi: {data.get('message', 'Không thể lấy danh sách tài khoản')}"))
            return None
    except Exception as e:
        print(error_color(f"Lỗi khi kiểm tra tài khoản TikTok: {str(e)}"))
        return None

# Get job from GoLike
def get_job(account_id):
    params = {'account_id': account_id, 'data': 'null'}
    try:
        response = requests.get('https://gateway.golike.net/api/advertising/publishers/tiktok/jobs', params=params, headers=headers, json={}, timeout=5)
        data = response.json()
        if data.get('status') == 400:
            print(error_color("Hết job để làm, chờ load lại sau..."))
            return None
        if data.get('success'):
            link = data['data']['link']
            job_id = data['data']['id']
            task_type = data['data']['type']
            object_id = data['data']['object_id']
            price = data['data']['price_per_after_cost']
            return link, job_id, task_type, object_id, price
        else:
            print(error_color(f"Lỗi: {data.get('message', 'Không thể lấy job')}"))
            return None
    except Exception as e:
        print(error_color(f"Lỗi khi lấy job: {str(e)}"))
        return None

# Verify job completion
def verify_complete_job(ads_id, account_id):
    global total_price
    json_data = {
        'ads_id': ads_id,
        'account_id': account_id,
        'async': True,
        'data': None,
    }
    try:
        response = requests.post('https://gateway.golike.net/api/advertising/publishers/tiktok/complete-jobs', headers=headers, json=json_data, timeout=5)
        data = response.json()
        if data.get('success'):
            price = data['data']['prices']
            total_price += price
            print(success_color(f"Xác minh thành công! Nhận {price}đ | Tổng: {total_price}đ"))
            return True
        else:
            print(error_color(f"Xác minh thất bại: {data.get('message', 'Không rõ nguyên nhân')}"))
            return False
    except Exception as e:
        print(error_color(f"Lỗi khi xác minh: {str(e)}"))
        return False

# Drop job if verification fails
def drop_job(ads_id, object_id, account_id, task_type):
    try:
        json_data1 = {
            'description': 'Tôi đã làm Job này rồi',
            'users_advertising_id': ads_id,
            'type': 'ads',
            'provider': 'tiktok',
            'fb_id': account_id,
            'error_type': 6,
        }
        requests.post('https://gateway.golike.net/api/report/send', headers=headers, json=json_data1, timeout=5)
        json_data2 = {
            'ads_id': ads_id,
            'object_id': object_id,
            'account_id': account_id,
            'type': task_type,
        }
        response = requests.post('https://gateway.golike.net/api/advertising/publishers/tiktok/skip-jobs', headers=headers, json=json_data2, timeout=5)
        if response.status_code == 200:
            print(success_color("Đã báo lỗi và bỏ job thành công"))
            return True
        else:
            print(error_color("Lỗi khi bỏ job"))
            return False
    except Exception as e:
        print(error_color(f"Lỗi khi bỏ job: {str(e)}"))
        return False

# Main program
os.system('clear')
banner = r'''
 ██████╗  ██████╗ ██╗     ██╗██╗  ██╗███████╗
██╔════╝ ██╔═══██╗██║     ██║██║ ██╔╝██╔════╝
██║  ███╗██║   ██║██║     ██║█████╔╝ █████╗  
██║   ██║██║   ██║██║     ██║██╔═██╗ ██╔══╝  
╚██████╔╝╚██████╔╝███████╗██║██║  ██╗███████╗
 ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝╚══════╝
'''
gach = '========================================='
option = f'''{gach}{Colors.green}
Danh sách nhiệm vụ hỗ trợ: {Colors.red}
1. Follow
2. Like
3. Follow + Like
{Colors.yellow}{gach}
'''
print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(banner)))
print(Colors.red + Center.XCenter(Box.DoubleCube("Tool GoLike TikTok for Termux v1.0")))

# Load or input credentials
auth, t = load_credentials()
headers['Authorization'] = auth
headers['t'] = t

# Check TikTok accounts
while True:
    accounts = check_tiktok_account(auth, t)
    if accounts:
        try:
            choice = int(Write.Input("Chọn số thứ tự tài khoản TikTok: ", Colors.green_to_yellow, interval=0.0025))
            if 1 <= choice <= len(accounts):
                account_id, username = accounts[choice - 1]
                print(success_color(f"Đã chọn tài khoản: {username} (ID: {account_id})"))
                break
            else:
                os.system('clear')
                print(error_color("Lựa chọn không hợp lệ! Vui lòng chọn số trong danh sách."))
        except:
            os.system('clear')
            print(error_color("Vui lòng nhập một số hợp lệ!"))
    else:
        print(error_color("Không tìm thấy tài khoản TikTok, kiểm tra lại token!"))
        os.remove('Authorization.txt')
        os.remove('token.txt')
        auth, t = load_credentials()
        headers['Authorization'] = auth
        headers['t'] = t

# Select task type
while True:
    os.system('clear')
    print(option)
    try:
        task_choice = int(Write.Input("Chọn nhiệm vụ (1: Follow, 2: Like, 3: Follow + Like): ", Colors.green_to_yellow, interval=0.0025))
        if task_choice in [1, 2, 3]:
            break
        else:
            print(error_color("Lựa chọn không hợp lệ! Chỉ nhập 1, 2 hoặc 3."))
    except:
        print(error_color("Vui lòng nhập một số hợp lệ!"))

# Input delay
while True:
    try:
        delay = int(Write.Input("Thời gian delay giữa các job (giây, tối thiểu 10): ", Colors.green_to_yellow, interval=0.0025))
        if delay >= 10:
            break
        else:
            os.system('clear')
            print(error_color("Delay tối thiểu là 10 giây!"))
    except:
        os.system('clear')
        print(error_color("Vui lòng nhập một số hợp lệ!"))

# Input max jobs
while True:
    try:
        max_jobs = int(Write.Input("Dừng lại khi làm được số nhiệm vụ (tối thiểu 10): ", Colors.green_to_yellow, interval=0.0025))
        if max_jobs >= 10:
            break
        else:
            os.system('clear')
            print(error_color("Tối thiểu là 10 nhiệm vụ!"))
    except:
        os.system('clear')
        print(error_color("Vui lòng nhập một số hợp lệ!"))

# Input max failures before stopping
while True:
    try:
        max_failures = int(Write.Input("Dừng lại sau bao nhiêu lần thất bại xác minh (tối thiểu 5): ", Colors.green_to_yellow, interval=0.0025))
        if max_failures >= 5:
            break
        else:
            os.system('clear')
            print(error_color("Tối thiểu là 5 lần thất bại!"))
    except:
        os.system('clear')
        print(error_color("Vui lòng nhập một số hợp lệ!"))

# Set allowed tasks
allowed_tasks = ['follow'] if task_choice == 1 else ['like'] if task_choice == 2 else ['follow', 'like']

# Initialize counters
total_price = 0
job_count = 0
failure_count = 0

# Main job loop
os.system('clear')
print(success_color(f"Bắt đầu làm việc với tài khoản: {username}"))
while job_count < max_jobs:
    if failure_count >= max_failures:
        print(error_color(f"Đã đạt {max_failures} lần thất bại xác minh, dừng chương trình!"))
        break

    print(system_color("Đang lấy nhiệm vụ..."), end="\r")
    result = get_job(account_id)
    if not result:
        print(system_color("Chờ 10 giây để thử lại..."))
        time.sleep(10)
        continue

    link, job_id, task_type, object_id, price = result
    if task_type not in allowed_tasks:
        print(error_color(f"Nhiệm vụ '{task_type}' không được chọn, bỏ qua..."))
        drop_job(job_id, object_id, account_id, task_type)
        time.sleep(2)
        continue

    t_now = datetime.now().strftime("%H:%M:%S")
    print(info_color(f"Job {job_count + 1}/{max_jobs} | {t_now} | Loại: {task_type} | ID: {job_id} | Tiền: {price}đ"))
    print(info_color(f"Link: {link}"))

    # Open TikTok link
    if task_type == "follow":
        username_tiktok = link.split("/")[-1].lstrip("@") if "/video/" not in link else link.split("/")[-3].lstrip("@")
        link = f"https://www.tiktok.com/@{username_tiktok}"
    os.system(f'termux-open-url "{link}"')
    time.sleep(5)

    # Simulate action (tap for follow/like)
    if task_type == "follow":
        os.system("input tap 540 650")  # Adjust coordinates as needed
    elif task_type == "like":
        os.system("input tap 540 1000")  # Adjust coordinates for like button
    time.sleep(2)

    # Verify job
    print(system_color(f"Chờ {delay} giây trước khi xác minh..."))
    time.sleep(delay)
    if verify_complete_job(job_id, account_id):
        job_count += 1
        failure_count = 0
    else:
        print(error_color("Bỏ job do xác minh thất bại..."))
        drop_job(job_id, object_id, account_id, task_type)
        failure_count += 1

    # Delay between jobs
    for i in range(delay, -1, -1):
        print(info_color(f"Vui lòng đợi: {i} giây"), end='\r')
        time.sleep(1)

print(success_color(f"Hoàn thành {job_count} nhiệm vụ! Tổng tiền: {total_price}đ"))
