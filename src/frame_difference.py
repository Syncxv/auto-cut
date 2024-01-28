import cv2
from utils import measure, write_text_to_file, format_timestamp_from_decimal, get_frame_rate

@measure
def extract_frames(video_path, n):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for frame_index in range(0, total_frames, n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    return frames


def resize_frame(frame, scale=0.5):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def convert_to_grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def is_scene_change(frame1, frame2, threshold):
    frame1_small_gray = convert_to_grayscale(resize_frame(frame1))
    frame2_small_gray = convert_to_grayscale(resize_frame(frame2))
    diff = cv2.absdiff(frame1_small_gray, frame2_small_gray)
    non_zero_count = cv2.countNonZero(diff)
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
    threshold = 50000

    scene_changes = detect_scene_changes("D:\\DownloadsGang\\media\\fam guy\\Family Guy - S08E18 - Quagmire's Dad.mp4", threshold, 125)

    write_text_to_file("\n".join(scene_changes), "./test/scene_changes.srt")


if __name__ == "__main__":
    main()