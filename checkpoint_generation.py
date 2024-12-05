import cv2
import numpy as np

# Load the image
image_path = 'track.png'  # Replace with your image path
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Threshold the image to detect the white track
_, track_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

# Find all contours, including the inner ones
contours, hierarchy = cv2.findContours(track_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

# Separate outer and inner contours
outer_contour = None
inner_contour = None

for idx, contour in enumerate(contours):
    if hierarchy[0][idx][3] == -1:  # Outer contour
        outer_contour = contour
    else:  # Inner contour
        inner_contour = contour

# Create a new image for visualization
checkpoint_image = image.copy()

# Number of checkpoints
num_checkpoints = 300

# Calculate cumulative arc lengths along the outer contour
outer_length = cv2.arcLength(outer_contour, True)
distances = np.linspace(0, outer_length, num_checkpoints + 1)[:-1]  # Exclude the last point

# Interpolate points along the outer contour
def interpolate_along_contour(contour, distances):
    points = []
    total_length = 0

    for i in range(1, len(contour)):
        pt1 = contour[i - 1][0]
        pt2 = contour[i][0]
        segment_length = np.linalg.norm(np.array(pt1) - np.array(pt2))
        while total_length + segment_length >= distances[0]:
            t = (distances[0] - total_length) / segment_length
            interpolated_point = (1 - t) * np.array(pt1) + t * np.array(pt2)
            points.append(interpolated_point.astype(int))
            distances = distances[1:]
            if len(distances) == 0:
                return points
        total_length += segment_length

    return points

evenly_spaced_points = interpolate_along_contour(outer_contour, distances)

# Function to find the closest point on the inner contour to a given point
def find_closest_point(point, contour):
    min_dist = float('inf')
    closest_point = None
    for cpt in contour:
        dist = np.linalg.norm(np.array(point) - np.array(cpt[0]))
        if dist < min_dist:
            min_dist = dist
            closest_point = cpt[0]
    return closest_point

# Draw checkpoints from the outer to the inner contour and enumerate them
for idx, outer_point in enumerate(evenly_spaced_points):
    outer_point = tuple(outer_point)
    inner_point = tuple(map(int, find_closest_point(outer_point, inner_contour)))
    
    # Draw the checkpoint line
    cv2.line(checkpoint_image, outer_point, inner_point, (255, 0, 0), 2)
    
    # Enumerate the checkpoint at its midpoint
    midpoint = ((outer_point[0] + inner_point[0]) // 2, (outer_point[1] + inner_point[1]) // 2)
    cv2.putText(checkpoint_image, str(idx + 1), midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

# Save the result
output_path = 'track_with_numbered_checkpoints_fixed.png'
cv2.imwrite(output_path, checkpoint_image)
