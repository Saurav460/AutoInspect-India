import cv2
import numpy as np


# Load before and after images
before = cv2.imread("before.jpg")
after = cv2.imread("after.jpg")


# Check that both images loaded
if before is None or after is None:
    print("Could not load one or both images.")
    raise SystemExit


# Make sure both images have same dimensions
if before.shape != after.shape:
    print("Images have different dimensions.")
    raise SystemExit


# Calculate absolute pixel difference
difference = cv2.absdiff(before, after)


# Convert difference to grayscale
gray_difference = cv2.cvtColor(
    difference,
    cv2.COLOR_BGR2GRAY
)


# Create a binary mask
_, threshold = cv2.threshold(
    gray_difference,
    30,
    255,
    cv2.THRESH_BINARY
)


# Find changed regions
contours, _ = cv2.findContours(
    threshold,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)


print("\n===== IMAGE DIFFERENCE RESULT =====")

changed_regions = 0

for contour in contours:

    area = cv2.contourArea(contour)

    # Ignore tiny changes/noise
    if area < 50:
        continue

    x, y, width, height = cv2.boundingRect(contour)

    changed_regions += 1

    print("\nChanged Region:", changed_regions)
    print("X:", x)
    print("Y:", y)
    print("Width:", width)
    print("Height:", height)
    print("Area:", round(area, 2))


if changed_regions == 0:
    print("\nNo significant image change detected.")

else:
    print(
        f"\nTotal changed regions: {changed_regions}"
    )


print("\n===================================")