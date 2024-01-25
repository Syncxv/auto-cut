from utils import timestamp_to_seconds

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
