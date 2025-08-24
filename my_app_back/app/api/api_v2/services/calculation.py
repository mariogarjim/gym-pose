import numpy as np


class CalculationService:
    def scale_point(self, point, image_shape):
        h, w = image_shape[:2]
        return (int(point[0] * w), int(point[1] * h))

    def squat_back_posture_calculations(self, shoulder, hip, frame_shape) -> int:
        shoulder = self.scale_point(shoulder, frame_shape)
        hip = self.scale_point(hip, frame_shape)

        torso_vec = np.array(shoulder) - np.array(hip)
        # Normalize the vector to get only the direction
        torso_norm = np.linalg.norm(torso_vec)
        torso_norm_is_zero = torso_norm < 1e-6

        if not torso_norm_is_zero:
            vertical_vec = np.array([0, -1])  # Opposite to gravity vector
            cos_theta = np.dot(torso_vec, vertical_vec) / torso_norm
            raw_angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
            angle_deg = int(min(raw_angle, 180 - raw_angle))

        return angle_deg

    def squat_depth_calculations(self, hip, knee, frame_shape) -> int:
        hip = self.scale_point(hip, frame_shape)
        knee = self.scale_point(knee, frame_shape)

        depth = hip[1] - knee[1]
        return depth

    def squat_head_alignment_calculations(self, ear, shoulder, frame_shape) -> float:
        ear = self.scale_point(ear, frame_shape)
        shoulder = self.scale_point(shoulder, frame_shape)

        horizontal_offset = ear[0] - shoulder[0]
        return horizontal_offset
