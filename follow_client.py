import socket
import time
import os
import sys

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

def send_follow_request(host='127.0.0.1', port=12345):
    """Gửi yêu cầu Follow đến server trên PC và nhận kết quả"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        log(f"Kết nối đến server tại {host}:{port}")
        
        # Gửi yêu cầu Follow
        client.send("FOLLOW".encode('utf-8'))
        log("Đã gửi yêu cầu Follow")
        
        # Nhận kết quả
        result = client.recv(1024).decode('utf-8')
        log(f"Kết quả từ server: {result}")
        return result
    except Exception as e:
        log(f"Lỗi khi gửi yêu cầu: {e}")
        return f"Error: {str(e)}"
    finally:
        client.close()

def main():
    result = send_follow_request()
    log(f"Kết quả cuối cùng: {result}")

if __name__ == "__main__":
    main()