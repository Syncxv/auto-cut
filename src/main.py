import subtitle
import frame_difference
import utils

def main():
    [video_path] = utils.get_args()
    subtitle_timestamps = subtitle.detect_subtitle_pauses(video_path)
    scene_change_timestamps = frame_difference.detect_scene_changes(video_path, 0.29, 24)

    tolerance_seconds = 4
    frame_rate = utils.get_frame_rate(video_path)

    # Tag each timestamp with its type
    all_timestamps = [(utils.timestamp_to_seconds(ts, frame_rate), 'pause') for ts in subtitle_timestamps] + \
                     [(utils.timestamp_to_seconds(ts, frame_rate), 'visual') for ts in scene_change_timestamps]

    # Sort the timestamps
    all_timestamps.sort()

    consolidated_timestamps = []
    i = 0

    while i < len(all_timestamps):
        current_timestamp, current_type = all_timestamps[i]
        range_end = i + 1
        has_both_types = current_type != 'both'  # Starts as False if 'both', True otherwise

        # Check timestamps within the tolerance range
        while range_end < len(all_timestamps) and all_timestamps[range_end][0] - current_timestamp <= tolerance_seconds:

            print(range_end, all_timestamps[range_end][0] - current_timestamp, tolerance_seconds)
            if all_timestamps[range_end][1] != current_type:
                has_both_types = True  # Found both types within the range
            range_end += 1

        # Only add to the list if both types of timestamps are found
        if has_both_types:
            consolidated_timestamp = sum(t[0] for t in all_timestamps[i:range_end]) / (range_end - i)
            consolidated_timestamps.append(consolidated_timestamp)

        i = range_end

    converted_timestamps = map(lambda ts: utils.format_timestamp_from_decimal(ts), consolidated_timestamps)
    utils.write_text_to_file("\n".join(converted_timestamps), "./test/consolidated_timestamps.srt")


if __name__ == "__main__":
    main()
