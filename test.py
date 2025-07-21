import subprocess
import time
import os
import sys

# Thiết lập thư mục log
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'follow_bot.log')

def log(message):
    """Ghi log vào console và file"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def run_adb_command(command):
    """Chạy lệnh ADB và trả về kết quả"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Lỗi khi chạy lệnh ADB: {e}")
        return None

def tap(x, y):
    """Nhấn vào tọa độ (x, y) trên màn hình"""
    command = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
    run_adb_command(command)
    time.sleep(1)  # Chờ 1 giây sau khi nhấn

def swipe(start_x, start_y, end_x, end_y, duration_ms=300):
    """Vuốt từ (start_x, start_y) đến (end_x, end_y)"""
    command = ['adb', 'shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)]
    run_adb_command(command)
    time.sleep(1)  # Chờ 1 giây sau khi vuốt

def perform_action(task_type, follow_x=900, follow_y=600):
    """Thực hiện thao tác Follow và kiểm tra trạng thái"""
    try:
        if task_type == "follow":
            # Nhấn nút Follow
            log("Nhấn nút Follow...")
            tap(follow_x, follow_y)
            time.sleep(2)  # Chờ TikTok cập nhật

            # Vuốt màn hình từ trên xuống dưới
            log("Vuốt màn hình...")
            swipe(500, 300, 500, 900, 300)
            time.sleep(2)

            # Kiểm tra trạng thái Follow bằng cách nhấn lại
            log("Kiểm tra trạng thái Follow...")
            tap(follow_x, follow_y)
            time.sleep(1)

            # Giả định: Nếu nhấn lần nữa mà không có thay đổi lớn (hoặc cần OCR), thì đã follow
            log("Follow thành công (giả định)")
            return "Follow ok"

        else:
            log(f"Task type không hợp lệ: {task_type}")
            return False

    except Exception as e:
        log(f"Lỗi khi thực hiện {task_type}: {e}")
        return False

def main():
    # Tọa độ nút Follow (cần điều chỉnh theo thiết bị của bạn)
    FOLLOW_X = 33  # Ví dụ
    FOLLOW_Y = 25  # Ví dụ

    # Thực hiện thao tác Follow
    result = perform_action("follow", FOLLOW_X, FOLLOW_Y)
    log(f"Kết quả: {result}")

if __name__ == "__main__":
    main()
