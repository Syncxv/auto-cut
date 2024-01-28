import sys
import time
import os

def timestamp_to_seconds(timestamp, framerate=24.0):
    h, m, s, f = map(int, timestamp.split(':'))
    return h * 3600 + m * 60 + s + f / framerate

def format_timestamp_from_decimal(timestamp):
    hours = int(timestamp / 3600)
    minutes = int(timestamp / 60) % 60
    seconds = int(timestamp) % 60
    milliseconds = int((timestamp - int(timestamp)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

def format_timestamp_from_frames(frame_number, frame_rate):
    timestamp = frame_number / frame_rate
    return format_timestamp_from_decimal(timestamp)

def milliseconds_to_frames(milliseconds, frame_rate):
    frames = int((milliseconds / 1000) * frame_rate + 0.5)
    return frames

def get_args():
    args = sys.argv[1:]
    if len(args) != 1:
        return ["D:\\DownloadsGang\\media\\fam guy\\Family Guy - S08E18 - Quagmire's Dad.mp4"]
    return args

def write_text_to_file(text, file_path):
    with open(file_path, "w") as f:
        f.write(text)

def read_text_from_file(file_path):
    with open(file_path, "r", -1, "utf-8") as f:
        return f.read()

def measure(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to execute.")
        return result
    return wrapper


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)