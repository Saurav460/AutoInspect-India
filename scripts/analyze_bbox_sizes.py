from pathlib import Path
from collections import defaultdict

LABEL_DIR = Path(r"S:\WEB DEVELOPEMENT\AutoInspect-India\dataset\labels\train")

CLASS_NAMES = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat"
}

data = defaultdict(list)

for label_file in LABEL_DIR.glob("*.txt"):
    with open(label_file, "r") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])
            width = float(parts[3])
            height = float(parts[4])

            area = width * height

            data[class_id].append((width, height, area))

print("\nCLASS-WISE BOUNDING BOX ANALYSIS")
print("=" * 70)

for class_id in sorted(CLASS_NAMES):
    boxes = data[class_id]

    if not boxes:
        continue

    avg_width = sum(x[0] for x in boxes) / len(boxes)
    avg_height = sum(x[1] for x in boxes) / len(boxes)
    avg_area = sum(x[2] for x in boxes) / len(boxes)

    small_boxes = sum(1 for x in boxes if x[2] < 0.01)
    small_percentage = (small_boxes / len(boxes)) * 100

    print(f"\n{CLASS_NAMES[class_id]}")
    print(f"Boxes:            {len(boxes)}")
    print(f"Average width:    {avg_width:.4f}")
    print(f"Average height:   {avg_height:.4f}")
    print(f"Average area:     {avg_area:.6f}")
    print(f"Small boxes <1%:  {small_boxes} ({small_percentage:.2f}%)")

print("\n" + "=" * 70)