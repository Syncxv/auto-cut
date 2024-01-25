import json
import sys




def get_args():
    args = sys.argv[1:]
    if len(args) != 1:
        return ["./test/Family Guy - S08E18 - Quagmire's Dad.txt"]
    return args

def write_text_to_file(text, file_path):
    with open(file_path, "w") as f:
        f.write(text)

def read_text_from_file(file_path):
    with open(file_path, "r", -1, "utf-8") as f:
        return f.read()

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

def main():
    [subtitle_path] =  get_args()
    subtitle_text = read_text_from_file(subtitle_path)

    subtitles = parse_all_subtitles(subtitle_text)
    write_text_to_file(json.dumps(subtitles, indent=4), "./test/subtitles.json")

if __name__ == "__main__":
    main()

