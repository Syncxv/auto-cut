import cv2
from utils import measure, write_text_to_file, format_timestamp_from_decimal, get_frame_rate, get_video_duration, clean_frames_dir, read_text_from_file, ensure_dir
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
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
    frame = apply_gaussian_blur(frame)
    frame = convert_to_grayscale(frame)

    return frame

def is_scene_change(frame1, frame2, threshold, print_diff=False):
    frame1_hsv = process_frame(frame1)
    frame2_hsv = process_frame(frame2)

    ssim_index, _ = compare_ssim(frame1_hsv, frame2_hsv, full=True)

    if print_diff:
        print(ssim_index)

    return ssim_index < threshold


@measure
def detect_scene_changes(video_path, threshold=50000, n=125):
    frame_rate = get_frame_rate(video_path)
    frames = extract_frames_ffmpeg(video_path, n)
    scene_changes = []

    for i in range(1, len(frames)):
        if is_scene_change(frames[i-1], frames[i], threshold):
            frame_number = i * n
            timestamp = frame_number / frame_rate
            scene_changes.append(timestamp)

    return list(map(lambda ts: format_timestamp_from_decimal(ts, frame_rate), scene_changes))


def main():
    threshold = 0.31
    frame1 = cv2.imread("./dist/frames/frame_0511.jpg")
    frame2 = cv2.imread("./dist/frames/frame_0512.jpg")

    print(is_scene_change(frame1, frame2, threshold, True))

    frame1 = cv2.imread("./dist/frames/frame_0130.jpg")
    frame2 = cv2.imread("./dist/frames/frame_0131.jpg")

    print(is_scene_change(frame1, frame2, threshold, True))

    # scene_changes = detect_scene_changes("D:\\DownloadsGang\\media\\fam guy\\Family Guy - S08E18 - Quagmire's Dad.mp4", threshold, 24)

    # write_text_to_file("\n".join(scene_changes), "./test/scene_changes.srt")
    


if __name__ == "__main__":
    main()
