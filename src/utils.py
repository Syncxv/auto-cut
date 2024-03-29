import sys
import time
import os
import subprocess
import json

def timestamp_to_seconds(timestamp, framerate=24.0):
    h, m, s, f = map(int, timestamp.split(':'))
    return h * 3600 + m * 60 + s + f / framerate

def format_timestamp_from_decimal(timestamp, framerate=24.0):
    hours = int(timestamp / 3600)
    minutes = int(timestamp / 60) % 60
    seconds = int(timestamp) % 60
    frame = int((timestamp - int(timestamp)) * framerate)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frame:02d}"

def format_timestamp_from_frames(frame_number, frame_rate):
    timestamp = frame_number / frame_rate
    return format_timestamp_from_decimal(timestamp)

def milliseconds_to_frames(milliseconds, frame_rate):
    frames = int((milliseconds / 1000) * frame_rate + 0.5)
    return frames

def timestamp_to_ffmpeg_format(timestamp, frame_rate):
    hours, minutes, seconds, frames = map(int, timestamp.split(":"))
    frames_to_seconds = frames / frame_rate
    total_seconds = hours * 3600 + minutes * 60 + seconds + frames_to_seconds
    return f"{hours:02}:{minutes:02}:{seconds:02}.{int(frames_to_seconds * 1000):03}"
 

def get_args(count=3):
    args = sys.argv[1:]
    if len(args) != count:
        return ["D:\\DownloadsGang\\media\\fam guy\\Family Guy - S08E18 - Quagmire's Dad.mp4", .29, 24]
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

def memoize(func):
    cache = {}
    def wrapper(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def clean_frames_dir(path):
    if not path.endswith("/frames"):
        raise Exception("Path must end with '/frames'")
    ensure_dir(path)
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            os.remove(os.path.join(path, file))


def clean_cut_video_dir(path):
    if not path.endswith("/cut_video"):
        raise Exception("Path must end with '/cut_video'")
    ensure_dir(path)
    for file in os.listdir(path):
        if file.endswith(".mp4"):
            os.remove(os.path.join(path, file))
@memoize
def get_frame_rate(video_path):
    print("Getting frame rate...")
    output = subprocess.run(["ffprobe", "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", video_path], capture_output=True)
    return float(output.stdout.decode("utf-8").strip().split("/")[0])
    
@memoize
def get_video_duration(video_path):
    command = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "json", 
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    duration = json.loads(result.stdout)['format']['duration']
    return float(duration)


if __name__ == "__main__":
    print("This file is not meant to be run directly.")
    print("Please run main.py instead.")
    sys.exit(1)