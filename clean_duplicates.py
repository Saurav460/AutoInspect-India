from pathlib import Path
import shutil


labels_dir = Path("dataset/labels/val")
backup_dir = Path("dataset/labels/train_backup")

# Create backup folder
if not backup_dir.exists():
    print("Creating backup...")
    shutil.copytree(labels_dir, backup_dir)
    print("Backup created successfully!")
else:
    print("Backup already exists. No new backup created.")

files_changed = 0
duplicates_removed = 0

for file in labels_dir.glob("*.txt"):

    lines = [
        line.strip()
        for line in file.read_text().splitlines()
        if line.strip()
    ]

    unique_lines = []
    seen = set()

    for line in lines:
        if line not in seen:
            unique_lines.append(line)
            seen.add(line)
        else:
            duplicates_removed += 1

    if len(unique_lines) != len(lines):
        files_changed += 1

        file.write_text(
            "\n".join(unique_lines) + "\n"
        )

print("\n" + "=" * 45)
print("LABEL CLEANUP COMPLETE")
print("=" * 45)

print(f"Files changed       : {files_changed}")
print(f"Duplicates removed  : {duplicates_removed}")
print(f"Backup location     : {backup_dir}")