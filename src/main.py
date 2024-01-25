import json
from utils import get_args, read_text_from_file, write_text_to_file
from parse_subtitle import parse_all_subtitles


def main():
    [subtitle_path] =  get_args()
    subtitle_text = read_text_from_file(subtitle_path)

    subtitles = parse_all_subtitles(subtitle_text)
    write_text_to_file(json.dumps(subtitles, indent=4), "./test/subtitles.json")

if __name__ == "__main__":
    main()

