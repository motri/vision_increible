import numpy as np

def calculate_angle(point1, point2, point3):
    """Calculate the angle between three points."""
    a = np.array(point1)
    print(a)
    b = np.array(point2)
    print(b)
    c = np.array(point3)
    print(c)
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    print (np.degrees(angle))

    return np.degrees(angle)