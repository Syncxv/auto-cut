import json
from utils import get_args, read_text_from_file, write_text_to_file
from subtitle import parse_all_subtitles, get_pause_times


def main():
    [subtitle_path] =  get_args()
    subtitle_text = read_text_from_file(subtitle_path)

    subtitles = parse_all_subtitles(subtitle_text)
    write_text_to_file(json.dumps(subtitles, indent=4), "./test/subtitles.json")

    pauses = get_pause_times(subtitles)
    average_pause = sum(pause for pause, _ in pauses) / len(pauses)

    threshold = average_pause * 1.5

    for pause, count in pauses:
        if pause > threshold:
            index = subtitles.index(next(sub for sub in subtitles if sub["count"] == count))
            sub = subtitles[index]
            
            print(f"Pause {count}: {pause:.2f}s\ncut_timestamp: {sub['end_time']}\n\n")


if __name__ == "__main__":
    main()

