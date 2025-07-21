import subprocess
import time
import os
import sys
import re
from PIL import Image
import pytesseract

# Thiết lập thư mục log
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'follow_bot.log')

def log(message):
    """Ghi log vào console và file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")

def run_adb_command(command):
    """Chạy lệnh ADB và trả về kết quả"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Lỗi khi chạy lệnh ADB: {e}")
        return None

def get_screen_resolution():
    """Lấy độ phân giải màn hình bằng lệnh ADB"""
    output = run_adb_command(['adb', 'shell', 'wm', 'size'])
    if output:
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            width, height = map(int, match.groups())
            return width, height
    log("Không thể lấy độ phân giải màn hình, sử dụng mặc định 1080x1920")
    return 1080, 1920

def tap(x, y):
    """Nhấn vào tọa độ (x, y) trên màn hình"""
    command = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
    run_adb_command(command)
    time.sleep(1)

def swipe(start_x, start_y, end_x, end_y, duration_ms=300):
    """Vuốt từ (start_x, start_y) đến (end_x, end_y)"""
    command = ['adb', 'shell', 'input', 'swipe', str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)]
    run_adb_command(command)
    time.sleep(1)

def capture_screenshot():
    """Chụp ảnh màn hình và lưu vào /sdcard/screenshot.png"""
    screenshot_path = "/sdcard/screenshot.png"
    local_path = os.path.join(os.path.dirname(__file__), 'screenshot.png')
    run_adb_command(['adb', 'shell', 'screencap', screenshot_path])
    run_adb_command(['adb', 'pull', screenshot_path, local_path])
    return local_path, screenshot_path

def check_follow_status():
    """Kiểm tra trạng thái Follow bằng OCR"""
    try:
        local_path, remote_path = capture_screenshot()
        text = pytesseract.image_to_string(Image.open(local_path))
        if "Following" in text or "Friends" in text:
            return "Nhả follow"
        else:
            return "Follow ok"
    except Exception as e:
        log(f"Lỗi khi phân tích ảnh: {e}")
        return False
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
        run_adb_command(['adb', 'shell', 'rm', remote_path])

def perform_action(task_type, follow_x_percent=33, follow_y_percent=25):
    """Thực hiện thao tác Follow và kiểm tra trạng thái"""
    try:
        if task_type == "follow":
            # Lấy độ phân giải màn hình
            screen_width, screen_height = get_screen_resolution()
            follow_x = int(screen_width * (follow_x_percent / 100))
            follow_y = int(screen_height * (follow_y_percent / 100))

            # Nhấn nút Follow
            log("Nhấn nút Follow...")
            tap(follow_x, follow_y)
            time.sleep(2)  # Chờ TikTok cập nhật

            # Vuốt màn hình từ trên xuống dưới (tương đối)
            swipe_x = screen_width // 2
            swipe_start_y = int(screen_height * 0.2)  # 20% từ đỉnh
            swipe_end_y = int(screen_height * 0.8)    # 80% từ đỉnh
            log("Vuốt màn hình...")
            swipe(swipe_x, swipe_start_y, swipe_x, swipe_end_y, 300)
            time.sleep(2)

            # Kiểm tra trạng thái Follow
            log("Kiểm tra trạng thái Follow...")
            status = check_follow_status()
            if status:
                log(f"Kết quả: {status}")
                return status
            else:
                log("Không thể xác định trạng thái Follow")
                return False

        else:
            log(f"Task type không hợp lệ: {task_type}")
            return False

    except Exception as e:
        log(f"Lỗi khi thực hiện {task_type}: {e}")
        return False

def main():
    # Thực hiện thao tác Follow
    result = perform_action("follow", follow_x_percent=33, follow_y_percent=25)
    log(f"Kết quả cuối cùng: {result}")

if __name__ == "__main__":
    main()
