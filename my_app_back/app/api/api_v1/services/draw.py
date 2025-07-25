import math

import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import pose as mp_pose


class ColorsEnum:
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    PURPLE = (255, 0, 255)
    ORANGE = (0, 165, 255)
    GRAY = (128, 128, 128)


def scale_point(point, image_shape):
    h, w = image_shape[:2]
    return (int(point[0] * w), int(point[1] * h))


def draw_landmarks(frame: np.ndarray, landmarks: NormalizedLandmarkList):
    mp_drawing.draw_landmarks(
        frame,
        landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
    )


def draw_angle(frame: np.ndarray, A, B, C, color=(0, 255, 0), thickness=2):
    # Draw the two lines forming the angle
    cv2.line(frame, B, A, color, thickness)
    cv2.line(frame, B, C, color, thickness)

    # Compute the angle in degrees
    def angle_between(v1, v2):
        v1_u = v1 / np.linalg.norm(v1)
        v2_u = v2 / np.linalg.norm(v2)
        dot = np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)
        return np.degrees(np.arccos(dot))

    v1 = np.array(A) - np.array(B)
    v2 = np.array(C) - np.array(B)
    angle = angle_between(v1, v2)

    # Draw angle text
    mid = (B[0] + 10, B[1] - 10)
    cv2.putText(frame, f"{int(angle)}°", mid, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Optionally: draw a small arc (approximate)
    radius = 30
    angle1 = math.degrees(math.atan2(v1[1], v1[0]))
    angle2 = math.degrees(math.atan2(v2[1], v2[0]))

    # Normalize angles
    start_angle = angle1
    end_angle = angle2
    if end_angle < start_angle:
        start_angle, end_angle = end_angle, start_angle

    cv2.ellipse(frame, B, (radius, radius), 0, start_angle, end_angle, color, 1)


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)


#### SQUAT ####


def draw_back_posture(
    frame,
    shoulder,
    hip,
    arrow_length=100,
    torso_color=ColorsEnum.GREEN,
    gravity_color=ColorsEnum.BLUE,
    arc_color=ColorsEnum.YELLOW,
    thickness=2,
):
    shoulder = scale_point(shoulder, frame.shape)
    hip = scale_point(hip, frame.shape)

    # Convert points to int pixel coordinates
    shoulder = tuple(map(int, shoulder))
    hip = tuple(map(int, hip))
    h, w = frame.shape[:2]

    # 1. Draw torso line
    cv2.line(frame, shoulder, hip, torso_color, thickness)
    cv2.putText(
        frame,
        "Torso",
        midpoint(shoulder, hip),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        torso_color,
        1,
    )

    # 2. Draw vertical arrow DOWN from hip
    gravity_end = (hip[0], min(h, hip[1] + arrow_length))
    cv2.arrowedLine(frame, hip, gravity_end, gravity_color, thickness, tipLength=0.2)
    cv2.putText(
        frame,
        "Vertical",
        (hip[0] + 5, hip[1] + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        gravity_color,
        1,
    )

    # 2. Draw vertical arrow UP from hip
    gravity_end = (hip[0], max(0, hip[1] - arrow_length))
    cv2.arrowedLine(frame, hip, gravity_end, gravity_color, thickness, tipLength=0.2)
    cv2.putText(
        frame,
        "Vertical",
        (hip[0] + 5, hip[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        gravity_color,
        1,
    )

    # 3. Compute torso vector and angle with vertical
    torso_vec = np.array(shoulder) - np.array(hip)
    torso_norm = np.linalg.norm(torso_vec)
    angle_deg = 0
    if torso_norm > 1e-6:
        # Vertical up vector
        vertical_vec = np.array([0, -1])  # y- is up
        cos_theta = np.dot(torso_vec, vertical_vec) / torso_norm
        raw_angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
        angle_deg = int(min(raw_angle, 180 - raw_angle))  # Acute angle

    # 4. Draw arc from vertical (up) to torso
    arc_radius = 40
    torso_angle = math.degrees(math.atan2(torso_vec[1], torso_vec[0])) % 360
    vertical_angle = 270  # upward direction in OpenCV

    # Arc goes from vertical → torso (clockwise)
    start_angle = vertical_angle
    end_angle = torso_angle
    sweep = (end_angle - start_angle) % 360
    if sweep > 180:
        sweep = 360 - sweep
        start_angle, end_angle = end_angle, start_angle

    cv2.ellipse(
        frame,
        hip,
        (arc_radius, arc_radius),
        0,
        start_angle,
        end_angle,
        arc_color,
        2,
    )

    # 5. Display angle label above hip
    cv2.putText(
        frame,
        f"{angle_deg} degrees",
        (hip[0] + arc_radius + 10, hip[1] - arc_radius - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        arc_color,
        2,
    )

    return angle_deg


def draw_squad_depth(
    frame, knee, hip, knee_color=(0, 255, 0), hip_color=(0, 0, 255), thickness=2
):
    """
    Dibuja una línea horizontal a la altura de la rodilla y un punto sobre la cadera.

    - frame: imagen (np.ndarray)
    - knee, hip: tuplas (x, y) en coordenadas normalizadas (0.0–1.0) o en píxeles
    """

    h, w = frame.shape[:2]

    # Convertir coordenadas normalizadas a píxeles si es necesario
    def to_px(pt):
        return (
            int(pt[0] * w) if 0 <= pt[0] <= 1 else int(pt[0]),
            int(pt[1] * h) if 0 <= pt[1] <= 1 else int(pt[1]),
        )

    knee_px = to_px(knee)
    hip_px = to_px(hip)

    # 1. Línea horizontal en la rodilla
    cv2.line(
        frame, (0, knee_px[1]), (w - 1, knee_px[1]), knee_color, thickness, cv2.LINE_AA
    )

    # 2. Punto en la cadera
    cv2.circle(frame, hip_px, 6, hip_color, -1, cv2.LINE_AA)

    # Etiquetas opcionales
    cv2.putText(
        frame,
        "Knee level",
        (10, knee_px[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        knee_color,
        1,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        "Hip",
        (hip_px[0] + 10, hip_px[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        hip_color,
        1,
        cv2.LINE_AA,
    )


def draw_head_alignment(
    frame, ear, shoulder, max_offset, color=(0, 255, 255), thickness=2
):
    """
    Draws a horizontal line from shoulder to ear to visualize head alignment.

    Parameters:
    - frame: OpenCV image
    - ear: (x, y) tuple (normalized [0–1] or pixels)
    - shoulder: (x, y) tuple (normalized [0–1] or pixels)
    - color: line color (default yellow)
    - thickness: line thickness
    """

    ear_px = scale_point(ear, frame.shape)
    shoulder_px = scale_point(shoulder, frame.shape)

    # 1. Draw line from shoulder to ear
    cv2.line(frame, shoulder_px, ear_px, color, thickness, cv2.LINE_AA)

    # 2. Mark points
    cv2.circle(frame, shoulder_px, 5, (0, 0, 255), -1)  # red
    cv2.circle(frame, ear_px, 5, (255, 0, 0), -1)  # blue

    # 3. Optional: annotate horizontal offset
    offset_px = ear_px[0] - shoulder_px[0]
    direction = "Forward" if offset_px > max_offset else "Correct"
    cv2.putText(
        frame,
        f"{direction} ({abs(offset_px)}px)",
        (shoulder_px[0] + 10, shoulder_px[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
        cv2.LINE_AA,
    )
