from ultralytics import YOLO


# ==========================================
# 1. LOAD TRAINED MODEL
# ==========================================

model = YOLO(r"runs\detect\train-5\weights\best.pt")


# ==========================================
# 2. CONFIDENCE THRESHOLD
# ==========================================

CONFIDENCE_THRESHOLD = 0.50


# ==========================================
# 3. SEVERITY ESTIMATION
# ==========================================

def estimate_severity(relative_area):

    if relative_area < 2:
        return "Minor"

    elif relative_area <= 10:
        return "Moderate"

    else:
        return "Severe"


# ==========================================
# 4. IMAGE LOCATION
# ==========================================

def get_image_location(center_x, center_y, image_width, image_height):

    # ------------------------------
    # Horizontal position
    # ------------------------------

    if center_x < image_width / 3:
        horizontal = "Left"

    elif center_x < (2 * image_width / 3):
        horizontal = "Center"

    else:
        horizontal = "Right"


    # ------------------------------
    # Vertical position
    # ------------------------------

    if center_y < image_height / 3:
        vertical = "Top"

    elif center_y < (2 * image_height / 3):
        vertical = "Middle"

    else:
        vertical = "Bottom"


    return f"{vertical}-{horizontal}"


# ==========================================
# 5. RUN PREDICTION
# ==========================================

results = model(
    r"dataset\images\test\000012.jpg",
    conf=CONFIDENCE_THRESHOLD
)


# ==========================================
# 6. GET FIRST IMAGE RESULT
# ==========================================

result = results[0]


# ==========================================
# 7. GET ORIGINAL IMAGE DIMENSIONS
# ==========================================

image_height, image_width = result.orig_shape


# ==========================================
# 8. CALCULATE TOTAL IMAGE AREA
# ==========================================

image_area = image_width * image_height


# ==========================================
# 9. CHECK FOR DETECTIONS
# ==========================================

if len(result.boxes) == 0:

    print("\nNo reliable damage detected.")


else:

    print("\n===== AUTOINSPECT RESULT =====")

    # ======================================
    # 10. PROCESS EACH DETECTION
    # ======================================

    for box in result.boxes:

        # ------------------------------
        # Class ID
        # ------------------------------

        class_id = int(box.cls[0])


        # ------------------------------
        # Class name
        # ------------------------------

        class_name = model.names[class_id]


        # ------------------------------
        # Confidence
        # ------------------------------

        confidence = float(box.conf[0])


        # ------------------------------
        # Bounding Box
        # ------------------------------

        x1, y1, x2, y2 = box.xyxy[0].tolist()


        # ------------------------------
        # Box dimensions
        # ------------------------------

        box_width = x2 - x1
        box_height = y2 - y1


        # ------------------------------
        # Box area
        # ------------------------------

        box_area = box_width * box_height


        # ------------------------------
        # Relative area
        # ------------------------------

        relative_area = (box_area / image_area) * 100


        # ------------------------------
        # Bounding box center
        # ------------------------------

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2


        # ------------------------------
        # DEBUG VALUES
        # ------------------------------

        print("\n----- DEBUG INFORMATION -----")
        print("Image Width      :", image_width)
        print("Image Height     :", image_height)
        print("Center X         :", round(center_x, 2))
        print("Center Y         :", round(center_y, 2))
        print("Width / 3        :", round(image_width / 3, 2))
        print("2 * Width / 3    :", round(2 * image_width / 3, 2))
        print("Height / 3       :", round(image_height / 3, 2))
        print("2 * Height / 3   :", round(2 * image_height / 3, 2))


        # ------------------------------
        # Image location
        # ------------------------------

        location = get_image_location(
            center_x,
            center_y,
            image_width,
            image_height
        )


        # ------------------------------
        # Severity estimate
        # ------------------------------

        severity = estimate_severity(relative_area)


        # ==================================
        # 11. FINAL RESULT
        # ==================================

        print("\nDamage Type    :", class_name)

        print(
            "Confidence     :",
            round(confidence * 100, 2),
            "%"
        )

        print(
            "Bounding Box   :",
            [round(x, 2) for x in [x1, y1, x2, y2]]
        )

        print(
            "Box Width      :",
            round(box_width, 2),
            "px"
        )

        print(
            "Box Height     :",
            round(box_height, 2),
            "px"
        )

        print(
            "Relative Area  :",
            round(relative_area, 2),
            "%"
        )

        print(
            "Image Location :",
            location
        )

        print(
            "Visual Severity:",
            severity
        )


    print("\n==============================")