import utils
import subprocess
import os

def cut_video(video_path, timestmap_path_or_array):
    if isinstance(timestmap_path_or_array, str):
        timestamps = utils.read_text_from_file(timestmap_path_or_array).split("\n")
    else:
        timestamps = timestmap_path_or_array

    output_folder = "./dist/cut_video"
    utils.clean_cut_video_dir(output_folder)

    frame_rate = utils.get_frame_rate(video_path)
    
    for i, timestamp in enumerate(timestamps[:-1]):
        start_time = utils.timestamp_to_ffmpeg_format(timestamp.strip(), frame_rate)
        end_time = utils.timestamp_to_ffmpeg_format(timestamps[i + 1].strip(), frame_rate)

        output_filename = f"scene_{i}.mp4"
        output_path = os.path.join(output_folder, output_filename)

        command = [
            'ffmpeg',
            '-ss', start_time,
            '-to', end_time,
            '-i', video_path,
            '-c', 'copy',
            output_path
        ]

        datta = subprocess.run(command, capture_output=True)
        print(datta.stderr.decode("utf-8"))

        

def main():
    [video_path, timestamp_path] = utils.get_args(2)
    cut_video(video_path, timestamp_path)

if __name__ == "__main__":
    main()