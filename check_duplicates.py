from pathlib import Path

labels_dir = Path("dataset/labels/train")

total_files = 0
files_with_duplicates = 0
total_duplicate_lines = 0

for file in labels_dir.glob("*.txt"):
    total_files += 1

    lines = [
        line.strip()
        for line in file.read_text().splitlines()
        if line.strip()
    ]

    unique_lines = set(lines)

    duplicate_count = len(lines) - len(unique_lines)

    if duplicate_count > 0:
        files_with_duplicates += 1
        total_duplicate_lines += duplicate_count

        print(f"\n{file.name}")
        print(f"  Total annotations : {len(lines)}")
        print(f"  Unique annotations: {len(unique_lines)}")
        print(f"  Duplicates        : {duplicate_count}")

print("\n" + "=" * 40)
print("DUPLICATE LABEL SCAN COMPLETE")
print("=" * 40)

print(f"Total label files       : {total_files}")
print(f"Files with duplicates  : {files_with_duplicates}")
print(f"Total duplicate lines  : {total_duplicate_lines}")