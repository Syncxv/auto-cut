import cv2
from utils import measure, write_text_to_file, format_timestamp_from_decimal, get_frame_rate, get_video_duration, clean_frames_dir, read_text_from_file, ensure_dir
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
import json


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


def is_scene_change(frame1, frame2, threshold):
    diff = cv2.absdiff(frame1, frame2)

    # Split the difference image into its color channels
    b_diff, g_diff, r_diff = cv2.split(diff)

    # Calculate the sum of non-zero values for each channel
    b_non_zero = cv2.countNonZero(b_diff)
    g_non_zero = cv2.countNonZero(g_diff)
    r_non_zero = cv2.countNonZero(r_diff)

    # Sum up the non-zero values of all channels
    total_non_zero = b_non_zero + g_non_zero + r_non_zero

    # print(total_non_zero)

    return total_non_zero > threshold


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
    threshold = 275_000

    scene_changes = detect_scene_changes("D:\\DownloadsGang\\media\\fam guy\\Family Guy - S08E18 - Quagmire's Dad.mp4", threshold, 50)

    write_text_to_file("\n".join(scene_changes), "./test/scene_changes.srt")
    
    # frame1 = cv2.imread("./dist/frames/frame_0248.jpg")
    # frame2 = cv2.imread("./dist/frames/frame_0246.jpg")

    # print(is_scene_change(frame1, frame2, threshold))


if __name__ == "__main__":
    main()
