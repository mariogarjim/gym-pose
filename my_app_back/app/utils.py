import numpy as np


def calculate_angle(a, b, c):
    try:
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        # Ensure the cosine value is within valid range [-1, 1]
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.arccos(cosine_angle)
        return float(np.degrees(angle))
    except Exception as e:
        print(f"Error calculating angle: {e}")
        print(f"Points: a={a}, b={b}, c={c}")
        return 0.0
