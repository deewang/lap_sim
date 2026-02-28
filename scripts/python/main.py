import os
from image_processing import extract_centerline
from path_extraction import smooth_path
from scaling_utils import scale_to_meters
from export_utils import save_to_csv

# Resolve data directory relative to this script, regardless of working directory
_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(_HERE, "../../data/tracks"))

image_path = os.path.join(DATA_DIR, "raw/cleanAutocross2024.png")

# spa is low

points = extract_centerline(image_path, 'low', True)

points_smooth = smooth_path(points, True, [1, 1])

#start pixel:
# endurance2025[513, 68]
# endurance2023[515, 68]

points_scaled = scale_to_meters(points_smooth, 228/500, True)

# endurance 23 and 25 use 200/500 pixels per foot
# autocross 24 uses 228/500
# minispa: 500/3000

save_to_csv(points_scaled, os.path.join(DATA_DIR, "processed/autocross2024_scaled_track_points.csv"))


# cool addition:
#  make it start at a given point by painting it green on the image? usefull if we want specific start and automation.


