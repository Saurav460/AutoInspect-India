from pathlib import Path
from collections import Counter

labels_dir = Path("dataset/labels/train")

class_names = {
    0: "dent",
    1: "scratch",
    2: "crack",
    3: "glass shatter",
    4: "lamp broken",
    5: "tire flat"
}

counter = Counter()

for file in labels_dir.glob("*.txt"):
    for line in file.read_text().splitlines():
        line = line.strip()

        if line:
            class_id = int(line.split()[0])
            counter[class_id] += 1

print("\n" + "=" * 40)
print("CLASS DISTRIBUTION")
print("=" * 40)

total = sum(counter.values())

for class_id, name in class_names.items():
    count = counter[class_id]
    percentage = (count / total) * 100 if total else 0

    print(f"{name:15} : {count:5} ({percentage:.2f}%)")

print("-" * 40)
print(f"Total annotations : {total}")