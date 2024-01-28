import subtitle
import frame_difference
import utils

def main():
    [video_path] = utils.get_args()
    subtitle_timestamps = subtitle.detect_subtitle_pauses(video_path)
    scene_change_timestamps = frame_difference.detect_scene_changes(video_path)

    tolerance_seconds = 1.5

    frame_rate = utils.get_frame_rate(video_path)

    all_timestamps = [
        utils.timestamp_to_seconds(ts, frame_rate) for ts in subtitle_timestamps + scene_change_timestamps
    ]
    all_timestamps.sort()

    consolidated_timestamps = []
    i = 0

    while i < len(all_timestamps):
        current_timestamp = all_timestamps[i]
        range_end = i
        while range_end < len(all_timestamps) and all_timestamps[range_end] - current_timestamp <= tolerance_seconds:
            range_end += 1

        consolidated_timestamp = sum(all_timestamps[i:range_end]) / (range_end - i)
        consolidated_timestamps.append(consolidated_timestamp)

        i = range_end

    converted_timestamps = map(lambda ts: utils.format_timestamp_from_decimal(ts), consolidated_timestamps)
    utils.write_text_to_file("\n".join(converted_timestamps), "./test/consolidated_timestamps.srt")


if __name__ == "__main__":
    main()

