from utils import timestamp_to_seconds, get_args, read_text_from_file, write_text_to_file
import json
def parse_subtitle(subtitle_text: str):
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
        # print(line)
        sub = parse_subtitle(line)
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

def detect_subtitle_pauses(subtitle_path):
    subtitle_text = read_text_from_file(subtitle_path)

    subtitles = parse_all_subtitles(subtitle_text)
    write_text_to_file(json.dumps(subtitles, indent=4), "./test/subtitles.json")

    pauses = get_pause_times(subtitles)
    average_pause = sum(pause for pause, _ in pauses) / len(pauses)

    threshold = average_pause * 1.5

    cut_timestamps = []

    for pause, count in pauses:
        if pause > threshold:
            index = subtitles.index(next(sub for sub in subtitles if sub["count"] == count))
            sub = subtitles[index]
            
            print(f"Pause {count}: {pause:.2f}s\ncut_timestamp: {sub['end_time']}\n\n")
            cut_timestamps.append(sub["end_time"])

    write_text_to_file("\n".join(cut_timestamps), "./test/cut_timestamps.srt")

    return cut_timestamps