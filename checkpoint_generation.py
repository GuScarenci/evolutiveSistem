import cv2
import numpy as np
import json

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
num_checkpoints = 40

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

# Function to find the closest point on the inner contour to a given point, ensuring non-overlap
used_inner_points = []

def find_closest_non_overlapping_point(point, contour, min_distance=10):
    min_dist = float('inf')
    closest_point = None
    for cpt in contour:
        cpt_point = cpt[0]
        dist = np.linalg.norm(np.array(point) - np.array(cpt_point))
        if dist < min_dist and all(np.linalg.norm(np.array(cpt_point) - np.array(p)) > min_distance for p in used_inner_points):
            min_dist = dist
            closest_point = cpt_point
    if closest_point is not None:
        used_inner_points.append(closest_point)
    return closest_point

# List to store checkpoint data
checkpoints_data = []

checkpoint_width = 10  # Width of the checkpoint rectangles
for idx, outer_point in enumerate(evenly_spaced_points):
    outer_point = tuple(outer_point)
    inner_point = find_closest_non_overlapping_point(outer_point, inner_contour)
    
    if inner_point is None:
        continue  # Skip if no valid inner point is found

    inner_point = tuple(map(int, inner_point))

    # Calculate the vector perpendicular to the checkpoint line
    direction_vector = np.array(inner_point) - np.array(outer_point)
    perpendicular_vector = np.array([-direction_vector[1], direction_vector[0]])
    perpendicular_vector = checkpoint_width * perpendicular_vector / np.linalg.norm(perpendicular_vector)

    # Define rectangle corners
    p1 = (int(outer_point[0] + perpendicular_vector[0]), int(outer_point[1] + perpendicular_vector[1]))
    p2 = (int(outer_point[0] - perpendicular_vector[0]), int(outer_point[1] - perpendicular_vector[1]))
    p3 = (int(inner_point[0] - perpendicular_vector[0]), int(inner_point[1] - perpendicular_vector[1]))
    p4 = (int(inner_point[0] + perpendicular_vector[0]), int(inner_point[1] + perpendicular_vector[1]))
    rectangle = [p1, p2, p3, p4]

    # Save checkpoint data
    checkpoints_data.append({
        "id": idx + 1,
        "rectangle": rectangle
    })

    # Draw the filled rectangle
    cv2.fillPoly(checkpoint_image, [np.array(rectangle, dtype=np.int32)], (255, 0, 0))
    
    # Enumerate the checkpoint at its midpoint
    midpoint = ((outer_point[0] + inner_point[0]) // 2, (outer_point[1] + inner_point[1]) // 2)
    cv2.putText(checkpoint_image, str(idx + 1), midpoint, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

# Save the checkpoint data to a JSON file
output_json_path = "checkpoints.json"
with open(output_json_path, "w") as json_file:
    json.dump(checkpoints_data, json_file, indent=4)

# Save the visualization
output_image_path = 'track_with_rectangular_checkpoints.png'
cv2.imwrite(output_image_path, checkpoint_image)

print(f"Checkpoint data saved to {output_json_path}")
