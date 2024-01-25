import sys

def timestamp_to_seconds(timestamp, framerate=24.0):
    h, m, s, f = map(int, timestamp.split(':'))
    return h * 3600 + m * 60 + s + f / framerate



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

