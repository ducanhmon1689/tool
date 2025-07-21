import requests
import time
import os
import sys
import json

# Thiết lập thư mục log
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'follow_client.log')

def log(message):
    """Ghi log vào console và file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")

def send_follow_request(url='http://10.0.0.2:8000/follow'):
    """Gửi yêu cầu Follow đến web server trên PC và nhận kết quả"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {'task': 'FOLLOW'}
        log(f"Đang gửi yêu cầu đến {url}")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        log(f"Kết quả từ server: {result}")
        return result.get('result', 'Error: No result')
    except Exception as e:
        log(f"Lỗi khi gửi yêu cầu: {str(e)}")
        return f"Error: {str(e)}"

def main():
    result = send_follow_request()
    log(f"Kết quả cuối cùng: {result}")

if __name__ == "__main__":
    main()
