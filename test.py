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
log_file = os.path.join(log_dir, 'check_follow_bot.log')

def log(message):
    """Ghi log vào console và file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")

def run_termux_command(command):
    """Chạy lệnh Termux và trả về kết quả"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Lỗi khi chạy lệnh Termux: {e}")
        return None

def get_screen_resolution():
    """Lấy độ phân giải màn hình bằng Termux API"""
    output = run_termux_command("termux-toast | wm size")
    if output:
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            width, height = map(int, match.groups())
            return width, height
    log("Không thể lấy độ phân giải màn hình, sử dụng mặc định 1080x1920")
    return 1080, 1920

def capture_screenshot():
    """Chụp ảnh màn hình bằng Termux API"""
    screenshot_path = "/sdcard/screenshot.png"
    local_path = os.path.join(os.path.dirname(__file__), 'screenshot.png')
    run_termux_command(f"termux-toast | screencap -p {screenshot_path}")
    run_termux_command(f"cp {screenshot_path} {local_path}")
    return local_path, screenshot_path

def crop_image(image_path, x, y, width=200, height=100):
    """Cắt ảnh quanh khu vực nút Follow để cải thiện độ chính xác OCR"""
    try:
        img = Image.open(image_path)
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        right = min(img.width, x + width // 2)
        bottom = min(img.height, y + height // 2)
        cropped_img = img.crop((left, top, right, bottom))
        cropped_path = image_path.replace('.png', '_cropped.png')
        cropped_img.save(cropped_path)
        return cropped_path
    except Exception as e:
        log(f"Lỗi khi cắt ảnh: {e}")
        return None

def check_follow_status(follow_x_percent=33, follow_y_percent=25):
    """Kiểm tra trạng thái Follow bằng OCR"""
    try:
        # Lấy độ phân giải màn hình
        screen_width, screen_height = get_screen_resolution()
        follow_x = int(screen_width * (follow_x_percent / 100))
        follow_y = int(screen_height * (follow_y_percent / 100))

        # Chụp và cắt ảnh màn hình
        log("Chụp ảnh màn hình...")
        local_path, remote_path = capture_screenshot()
        cropped_path = crop_image(local_path, follow_x, follow_y)
        if not cropped_path:
            return False

        # Phân tích văn bản bằng OCR
        log("Phân tích trạng thái Follow...")
        text = pytesseract.image_to_string(Image.open(cropped_path)).strip().lower()
        log(f"Văn bản OCR: {text}")

        # Kiểm tra trạng thái
        if "following" in text or "friends" in text:
            return "Nhả follow"
        elif "follow" in text:
            return "Follow ok"
        else:
            log("Không nhận diện được trạng thái Follow")
            return False

    except Exception as e:
        log(f"Lỗi khi kiểm tra trạng thái: {e}")
        return False
    finally:
        # Xóa ảnh
        if os.path.exists(local_path):
            os.remove(local_path)
        if os.path.exists(cropped_path):
            os.remove(cropped_path)
        run_termux_command(f"rm {remote_path}")

def main():
    # Kiểm tra trạng thái Follow
    result = check_follow_status(follow_x_percent=33, follow_y_percent=25)
    log(f"Kết quả cuối cùng: {result}")

if __name__ == "__main__":
    main()
