
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

