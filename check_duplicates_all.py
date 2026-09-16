from pathlib import Path


# Folders to check
folders = {
    "TRAIN": Path("dataset/labels/train"),
    "VAL": Path("dataset/labels/val"),
    "TEST": Path("dataset/labels/test")
}


grand_total_files = 0
grand_total_duplicate_files = 0
grand_total_duplicates = 0


for split_name, labels_dir in folders.items():

    total_files = 0
    files_with_duplicates = 0
    total_duplicate_lines = 0

    print("\n" + "=" * 45)
    print(f"CHECKING {split_name}")
    print("=" * 45)

    if not labels_dir.exists():
        print(f"Folder not found: {labels_dir}")
        continue

    for file in labels_dir.glob("*.txt"):

        total_files += 1

        # Read all non-empty lines
        lines = [
            line.strip()
            for line in file.read_text().splitlines()
            if line.strip()
        ]

        # Remove exact duplicate lines only for comparison
        unique_lines = set(lines)

        duplicate_count = len(lines) - len(unique_lines)

        if duplicate_count > 0:
            files_with_duplicates += 1
            total_duplicate_lines += duplicate_count

            print(f"\n{file.name}")
            print(f"  Total annotations  : {len(lines)}")
            print(f"  Unique annotations  : {len(unique_lines)}")
            print(f"  Duplicates          : {duplicate_count}")

    # Print summary for this folder
    print("\n" + "-" * 45)
    print(f"{split_name} SUMMARY")
    print("-" * 45)

    print(f"Total label files      : {total_files}")
    print(f"Files with duplicates  : {files_with_duplicates}")
    print(f"Duplicate lines        : {total_duplicate_lines}")

    # Add to overall totals
    grand_total_files += total_files
    grand_total_duplicate_files += files_with_duplicates
    grand_total_duplicates += total_duplicate_lines


# Final overall result
print("\n" + "=" * 45)
print("OVERALL DUPLICATE LABEL SCAN")
print("=" * 45)

print(f"Total label files          : {grand_total_files}")
print(f"Files with duplicates      : {grand_total_duplicate_files}")
print(f"Total duplicate lines      : {grand_total_duplicates}")

print("\nScan complete! ✅")