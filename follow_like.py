import requests
import time
import os
import sys
import json
import subprocess

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

def main():
    result = send_follow_request()
    log(f"Kết quả cuối cùng: {result}")

if __name__ == "__main__":
    main()
