import cv2
from utils import measure, write_text_to_file, format_timestamp_from_decimal, get_frame_rate, clean_frames_dir
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

@measure
def extract_frames(video_path, n):
    clean_frames_dir("./dist/frames")
    data = subprocess.run([
        "ffmpeg",
        "-i", video_path,
        "-vf", f"select=not(mod(n\\,{n}))",
        "-vsync", "vfr",
        "-q:v", "50000",
        "dist/frames/frame_%04d.jpg",
        "-y"
    ])

    if data.returncode != 0:
        print("No frames found.")
        print(data.stderr)
        return None

    frames = os.listdir("./dist/frames")
    def read_frame(frame):
        return cv2.imread(f"./dist/frames/{frame}")

    with ThreadPoolExecutor(max_workers=6) as executor:
        frames = list(executor.map(read_frame, frames))

    return frames

def is_scene_change(frame1, frame2, threshold):
    diff = cv2.absdiff(frame1, frame2)
    non_zero_count = cv2.countNonZero(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY))
    return non_zero_count > threshold

@measure
def detect_scene_changes(video_path, threshold=50000, n=125):
    frame_rate = get_frame_rate(video_path)
    frames = extract_frames(video_path, n)
    scene_changes = []

    for i in range(1, len(frames)):
        if is_scene_change(frames[i-1], frames[i], threshold):
            frame_number = i * n
            timestamp = frame_number / frame_rate
            scene_changes.append(timestamp)

    return list(map(format_timestamp_from_decimal, scene_changes))

def main():
    threshold = 500000 

    scene_changes = detect_scene_changes("D:\\DownloadsGang\\media\\fam guy\\Family Guy - S08E18 - Quagmire's Dad.mp4", threshold, 75)

    write_text_to_file("\n".join(scene_changes), "./test/scene_changes.srt")


if __name__ == "__main__":
    main()