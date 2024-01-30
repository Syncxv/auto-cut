from utils import timestamp_to_seconds, ensure_dir, read_text_from_file, write_text_to_file, get_args, milliseconds_to_frames
import json
import subprocess
import re

def extract_subtitle_text(video_path):
    ensure_dir("dist")

    path_raw = "dist/subtitle_raw.srt"
    data = subprocess.run(["ffmpeg", "-i", video_path, "-map", "0:s:0", path_raw, "-y"])

    if data.returncode != 0:
        print("No subtitles found.")
        print(data.stderr)
        return None

    path_clean = "dist/subtitle_clean.srt"
    convert_subtitle_format(path_raw, path_clean, 24.0)

    return read_text_from_file(path_clean)

def convert_subtitle_format(input_file, output_file, frame_rate):
    timestamp_regex = r"(\d{2}:\d{2}:\d{2}),(\d{3})"
    html_tag_regex = r"<[^>]+>"

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            def replace_timestamp(match):
                hours_minutes_seconds = match.group(1)
                milliseconds = int(match.group(2))
                frames = milliseconds_to_frames(milliseconds, frame_rate)
                return f"{hours_minutes_seconds}:{frames:02d}"

            line = re.sub(timestamp_regex, replace_timestamp, line)
            line = re.sub(html_tag_regex, '', line)
            outfile.write(line)

def parse_subtitle(subtitle_text: str):
    if subtitle_text == "":
        return None

    count, timestamps, *head = subtitle_text.split("\n")

    count = int(count)
    start_time, end_time = timestamps.split(" --> ")

    start_time = start_time.strip()
    end_time = end_time.strip()

    text = "\n".join(head)

    return {
        "count": count,
        "start_time": start_time,
        "end_time": end_time,
        "text": text
    }
    
def parse_all_subtitles(subtitle_text: str):
    result = []
    t = subtitle_text.split("\n\n")
    
    for line in t:
        sub = parse_subtitle(line)
        if sub is not None:
            result.append(sub)

    return result

def get_pause_times(subtitles):
    pauses = []

    for i in range(len(subtitles) - 1):
        sub = subtitles[i]
        next_sub = subtitles[i + 1]
        end_current = timestamp_to_seconds(sub["end_time"])
        start_next = timestamp_to_seconds(next_sub["start_time"])
        pauses.append((start_next - end_current, sub["count"]))


    return pauses

def detect_subtitle_pauses(video_path: str):
    subtitle_text = extract_subtitle_text(video_path,)

    if subtitle_text is None:
        print("No subtitles found.")
        return []

    subtitles = parse_all_subtitles(subtitle_text)
    write_text_to_file(json.dumps(subtitles, indent=4), "./test/subtitles.json")

    pauses = get_pause_times(subtitles)
    average_pause = sum(pause for pause, _ in pauses) / len(pauses)

    threshold = average_pause * 1.5

    cut_timestamps = []

    for pause, count in pauses:
        if pause > threshold:
            index = subtitles.index(next(sub for sub in subtitles if sub["count"]+1 == count))
            sub = subtitles[index]
            
            print(f"Pause {count}: {pause:.2f}s\ncut_timestamp: {sub['end_time']}\n")
            cut_timestamps.append(sub["end_time"])

    write_text_to_file("\n".join(cut_timestamps), "./test/cut_timestamps.srt")

    return cut_timestamps


def main():
    [video_path] = get_args()

    cut_timestamps = detect_subtitle_pauses(video_path)

    write_text_to_file("\n".join(cut_timestamps), "./test/cut_timestamps.srt")


if __name__ == "__main__":
    main()