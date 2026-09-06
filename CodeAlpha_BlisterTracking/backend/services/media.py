import cv2
import numpy as np


def resize_frame(frame, max_width=960):
    height, width = frame.shape[:2]
    scale = min(1.0, max_width / max(width, height))
    resized = (max(2, int(width * scale) // 2 * 2),
               max(2, int(height * scale) // 2 * 2))
    return cv2.resize(frame, resized) if resized != (width, height) else frame


def annotate(frame, tracks, show_trails=True):
    output = frame.copy()
    height, width = output.shape[:2]

    for track in tracks:
        identity = track["id"]
        color = (
            (identity * 47 + 60) % 180 + 60,
            (identity * 83) % 180 + 60,
            (identity * 31) % 180 + 60,
        )
        box = np.asarray(track["box"], dtype=float)
        box[[0, 2]] = np.clip(box[[0, 2]], 0, width - 1)
        box[[1, 3]] = np.clip(box[[1, 3]], 0, height - 1)
        x1, y1, x2, y2 = box.astype(int)

        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        label = f'blister  ID {identity}  {track["confidence"]:.2f}'
        (text_width, text_height), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        text_y = max(text_height + 8, y1)
        text_x = max(0, min(x1, width - text_width - 8))
        cv2.rectangle(
            output,
            (text_x, text_y - text_height - 8),
            (text_x + text_width + 8, text_y + 2),
            color,
            -1,
        )
        cv2.putText(
            output,
            label,
            (text_x + 4, text_y - 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (15, 20, 25),
            1,
            cv2.LINE_AA,
        )

        if show_trails and len(track["trail"]) > 1:
            points = np.asarray(track["trail"], dtype=np.int32)
            cv2.polylines(output, [points], False, color, 2)

    return output
