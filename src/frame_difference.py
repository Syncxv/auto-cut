import cv2
from utils import measure, write_text_to_file, format_timestamp_from_decimal, get_frame_rate, get_video_duration, clean_frames_dir, read_text_from_file, ensure_dir, get_args
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from skimage.metrics import structural_similarity as compare_ssim
import numpy as np



def apply_gaussian_blur(frame, kernel_size=(5, 5)):
    return cv2.GaussianBlur(frame, kernel_size, 0)

def convert_to_grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

@measure
def extract_frames_ffmpeg(video_path, n):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"select=not(mod(n\\,{n})), scale='min(350\\,iw):-1'",
        "-vsync", "vfr",
        "-q:v", "50000",
        "dist/frames/frame_%04d.jpg",
        "-y"
    ]

    frames_metadata = {
        "video_path": video_path,
        "frame_rate": get_frame_rate(video_path),
        "duration": get_video_duration(video_path),
        "ffmpeg_command": command,
        "n": n,
    }

    if os.path.exists("./dist/frames_metadata.json"):
        old_meta_data = json.loads(
            read_text_from_file("./dist/frames_metadata.json"))
        if old_meta_data == frames_metadata:
            print("Using cached frames.")
            return read_frames()

    ensure_dir("./dist")
    write_text_to_file(json.dumps(frames_metadata), "./dist/frames_metadata.json")

    clean_frames_dir("./dist/frames")
    data = subprocess.run(command)

    if data.returncode != 0:
        print("Error extracting frames.")
        print(data.stderr)
        return None

    return read_frames()


@measure
def read_frames():
    frames = os.listdir("./dist/frames")

    def read_frame(frame):
        return cv2.imread(f"./dist/frames/{frame}")

    with ThreadPoolExecutor(max_workers=6) as executor:
        frames = list(executor.map(read_frame, frames))

    return frames

def process_frame(frame):
    # frame = apply_gaussian_blur(frame)
    # frame = convert_to_grayscale(frame)

    return frame

def is_scene_change(frame1, frame2, threshold, print_diff=False):
    frame1_hsv = process_frame(frame1)
    frame2_hsv = process_frame(frame2)

    ssim_index, _ = compare_ssim(frame1_hsv, frame2_hsv, channel_axis=2, full=True)

    if print_diff:
        print(ssim_index)

    return ssim_index < threshold

def detect_scene_change_process_frame(frames, i, n, threshold, frame_rate):
    if is_scene_change(frames[i-1], frames[i], threshold):
        frame_number = i * n
        timestamp = frame_number / frame_rate
        return timestamp
    return None

@measure
def detect_scene_changes(video_path, threshold=50000, n=125):
    frame_rate = get_frame_rate(video_path)
    frames = extract_frames_ffmpeg(video_path, n)
    scene_changes = []

    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_index = {executor.submit(detect_scene_change_process_frame, frames, i, n, threshold, frame_rate): i for i in range(1, len(frames))}
        
        for future in as_completed(future_to_index):
            timestamp = future.result()
            if timestamp is not None:
                scene_changes.append(timestamp)

    return scene_changes


def group_timestamps(timestamps, threshold_seconds, frame_rate):
    grouped_timestamps = []
    current_group_start = None

    for ts_seconds in timestamps:
        
        if current_group_start is None:
            current_group_start = ts_seconds
        else:
            if ts_seconds - current_group_start <= threshold_seconds:
                continue
            else:
                grouped_timestamps.append(current_group_start)
                current_group_start = ts_seconds

    # Add the last group start if not added
    if current_group_start is not None:
        grouped_timestamps.append(current_group_start)

    return grouped_timestamps

def main():
    # threshold = 0.29
    # frame1 = cv2.imread("./dist/frames/frame_0511.jpg")
    # frame2 = cv2.imread("./dist/frames/frame_0512.jpg")

    # print(is_scene_change(frame1, frame2, threshold, True))

    # frame1 = cv2.imread("./dist/frames/frame_0130.jpg")
    # frame2 = cv2.imread("./dist/frames/frame_0131.jpg")

    # print(is_scene_change(frame1, frame2, threshold, True))

    [video_path, threshold, n] = get_args()

    frame_rate = get_frame_rate(video_path)
    scene_changes = detect_scene_changes(video_path, float(threshold), int(n))

    grouped_timestamps = group_timestamps(scene_changes, 8, frame_rate)
    final_timestamps = list(map(lambda ts: format_timestamp_from_decimal(ts, frame_rate), grouped_timestamps))
    
    print(final_timestamps)

    write_text_to_file("\n".join(final_timestamps), "./test/scene_changesBRUH.srt")
    


if __name__ == "__main__":
    main()
