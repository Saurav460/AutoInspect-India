import json

from ultralytics import YOLO


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_PATH = r"runs\detect\train-5\weights\best.pt"

BEFORE_IMAGE = "before_real_test.jpg"
AFTER_IMAGE = "after_real_test.jpg"

CONFIDENCE_THRESHOLD = 0.50
IOU_THRESHOLD = 0.50

OUTPUT_JSON = "inspection_result.json"


# ==========================================
# LOAD MODEL
# ==========================================

model = YOLO(MODEL_PATH)


# ==========================================
# IOU FUNCTION
# ==========================================

def calculate_iou(box1, box2):

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_width = max(0, x2 - x1)
    intersection_height = max(0, y2 - y1)

    intersection_area = (
        intersection_width * intersection_height
    )

    box1_area = (
        (box1[2] - box1[0])
        * (box1[3] - box1[1])
    )

    box2_area = (
        (box2[2] - box2[0])
        * (box2[3] - box2[1])
    )

    union_area = (
        box1_area
        + box2_area
        - intersection_area
    )

    if union_area == 0:
        return 0.0

    return intersection_area / union_area


# ==========================================
# GET DETECTIONS
# ==========================================

def get_detections(image_path):

    results = model(
        image_path,
        conf=CONFIDENCE_THRESHOLD,
        save=False
    )

    result = results[0]

    detections = []

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        detections.append({
            "class_id": class_id,
            "class_name": model.names[class_id],
            "confidence": confidence,
            "box": [x1, y1, x2, y2]
        })

    return detections


# ==========================================
# GET BEFORE / AFTER DETECTIONS
# ==========================================

before_detections = get_detections(BEFORE_IMAGE)

after_detections = get_detections(AFTER_IMAGE)


# ==========================================
# MATCH BEFORE → AFTER
# ==========================================

matched_after_indices = set()

existing_damage = []

potential_new_damage = []


for before in before_detections:

    best_iou = 0.0
    best_after_index = None

    for index, after in enumerate(after_detections):

        if index in matched_after_indices:
            continue

        # Same damage class only
        if before["class_id"] != after["class_id"]:
            continue

        iou = calculate_iou(
            before["box"],
            after["box"]
        )

        if iou > best_iou:
            best_iou = iou
            best_after_index = index

    # Matching existing damage
    if (
        best_after_index is not None
        and best_iou >= IOU_THRESHOLD
    ):

        matched_after_indices.add(best_after_index)

        matched = after_detections[best_after_index]

        existing_damage.append({
            "type": matched["class_name"],
            "confidence": round(
                matched["confidence"],
                4
            ),
            "iou": round(
                best_iou,
                4
            )
        })


# ==========================================
# FIND POTENTIAL NEW DAMAGE
# ==========================================

for index, after in enumerate(after_detections):

    if index in matched_after_indices:
        continue

    # Ignore low-confidence predictions
    if after["confidence"] < CONFIDENCE_THRESHOLD:
        continue

    potential_new_damage.append({
        "type": after["class_name"],
        "confidence": round(
            after["confidence"],
            4
        ),
        "bounding_box": [
            round(value, 2)
            for value in after["box"]
        ]
    })


# ==========================================
# OVERALL STATUS
# ==========================================

if potential_new_damage:

    overall_status = "Potential New Damage Detected"

else:

    overall_status = "No Potential New Damage Detected"


# ==========================================
# CREATE FINAL RESULT
# ==========================================

inspection_result = {

    "before_image": BEFORE_IMAGE,

    "after_image": AFTER_IMAGE,

    "existing_damage": existing_damage,

    "potential_new_damage": potential_new_damage,

    "summary": {
        "existing_damage_count": len(existing_damage),
        "potential_new_damage_count": len(
            potential_new_damage
        ),
        "overall_status": overall_status
    }
}


# ==========================================
# SAVE JSON
# ==========================================

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        inspection_result,
        file,
        indent=4
    )


# ==========================================
# PRINT RESULT
# ==========================================

print("\n===== AUTOINSPECT JSON RESULT =====")

print(
    json.dumps(
        inspection_result,
        indent=4
    )
)

print(
    f"\nJSON saved to: {OUTPUT_JSON}"
)

print("\n====================================")