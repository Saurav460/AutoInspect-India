from pathlib import Path
from ultralytics import YOLO


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_PATH = r"runs\detect\train-5\weights\best.pt"
IMAGE_PATH = r"dataset\images\test\000042.jpg"
LABEL_PATH = r"dataset\labels\test\000042.txt"

CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.50

CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat"
}


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

    union_area = box1_area + box2_area - intersection_area

    if union_area == 0:
        return 0.0

    return intersection_area / union_area


# ==========================================
# LOAD MODEL
# ==========================================

model = YOLO(MODEL_PATH)


# ==========================================
# GET PREDICTIONS
# ==========================================

results = model(
    IMAGE_PATH,
    conf=CONFIDENCE_THRESHOLD,
    save=False
)

result = results[0]


# ==========================================
# GET IMAGE SIZE
# ==========================================

image_height, image_width = result.orig_shape


# ==========================================
# READ GROUND TRUTH
# ==========================================

ground_truth = []

with open(LABEL_PATH, "r") as f:

    for line in f:

        parts = line.strip().split()

        if len(parts) != 5:
            continue

        class_id = int(parts[0])

        x_center = float(parts[1]) * image_width
        y_center = float(parts[2]) * image_height
        width = float(parts[3]) * image_width
        height = float(parts[4]) * image_height

        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2

        ground_truth.append({
            "class_id": class_id,
            "box": [x1, y1, x2, y2],
            "matched": False
        })


# ==========================================
# READ PREDICTIONS
# ==========================================

predictions = []

for box in result.boxes:

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    x1, y1, x2, y2 = box.xyxy[0].tolist()

    predictions.append({
        "class_id": class_id,
        "confidence": confidence,
        "box": [x1, y1, x2, y2]
    })


# ==========================================
# MATCH PREDICTIONS WITH GROUND TRUTH
# ==========================================

true_positives = []
false_positives = []

for prediction in predictions:

    best_iou = 0.0
    best_gt_index = None

    for i, gt in enumerate(ground_truth):

        if gt["matched"]:
            continue

        if gt["class_id"] != prediction["class_id"]:
            continue

        iou = calculate_iou(
            prediction["box"],
            gt["box"]
        )

        if iou > best_iou:
            best_iou = iou
            best_gt_index = i

    if (
        best_gt_index is not None
        and best_iou >= IOU_THRESHOLD
    ):

        ground_truth[best_gt_index]["matched"] = True

        true_positives.append({
            "class_id": prediction["class_id"],
            "confidence": prediction["confidence"],
            "iou": best_iou
        })

    else:

        false_positives.append(prediction)


# ==========================================
# FALSE NEGATIVES
# ==========================================

false_negatives = [
    gt for gt in ground_truth
    if not gt["matched"]
]


# ==========================================
# PRINT RESULTS
# ==========================================

print("\n===== SINGLE IMAGE EVALUATION =====")

print("\nGround Truth:", len(ground_truth))
print("Predictions :", len(predictions))

print("\nTrue Positives:", len(true_positives))

for item in true_positives:

    print(
        f"  {CLASS_NAMES[item['class_id']]} "
        f"| Confidence: {item['confidence']:.3f} "
        f"| IoU: {item['iou']:.3f}"
    )


print("\nFalse Positives:", len(false_positives))

for item in false_positives:

    print(
        f"  {CLASS_NAMES[item['class_id']]} "
        f"| Confidence: {item['confidence']:.3f}"
    )


print("\nFalse Negatives:", len(false_negatives))

for item in false_negatives:

    print(
        f"  {CLASS_NAMES[item['class_id']]}"
    )


print("\n==============================")