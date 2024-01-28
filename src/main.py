import json
from utils import get_args, read_text_from_file, write_text_to_file
from subtitle import parse_all_subtitles, get_pause_times, detect_subtitle_pauses


def main():
    [subtitle_path] = get_args()

    cut_timestamps = detect_subtitle_pauses(subtitle_path)

    write_text_to_file("\n".join(cut_timestamps), "./test/cut_timestamps.srt")


if __name__ == "__main__":
    main()

