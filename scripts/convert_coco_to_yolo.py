import json
import os
import shutil

category_mapping = {
    1: 0,  # dent
    2: 1,  # scratch
    3: 2,  # crack
    4: 3,  # glass shatter
    5: 4,  # lamp broken
    6: 5   # tire flat
}

base_path = r"C:\Users\91958\Downloads\CarDD_release\CarDD_release\CarDD_COCO"
project_path = r"S:\WEB DEVELOPEMENT\AutoInspect-India\dataset"


def convert_split(split):

    json_path = os.path.join(
        base_path,
        "annotations",
        f"instances_{split}2017.json"
    )

    image_input_path = os.path.join(
        base_path,
        f"{split}2017"
    )

    image_output_path = os.path.join(
        project_path,
        "images",
        split
    )

    label_output_path = os.path.join(
        project_path,
        "labels",
        split
    )

    os.makedirs(image_output_path, exist_ok=True)
    os.makedirs(label_output_path, exist_ok=True)

    with open(json_path, "r") as f:
        data = json.load(f)

    images = {img["id"]: img for img in data["images"]}

    annotation_count = 0

    for annotation in data["annotations"]:

        image_id = annotation["image_id"]

        if image_id not in images:
            continue

        image_info = images[image_id]

        file_name = image_info["file_name"]

        width = image_info["width"]
        height = image_info["height"]

        category_id = annotation["category_id"]

        if category_id not in category_mapping:
            continue

        class_id = category_mapping[category_id]

        x, y, bbox_width, bbox_height = annotation["bbox"]

        # COCO → YOLO
        x_center = x + bbox_width / 2
        y_center = y + bbox_height / 2

        x_center /= width
        y_center /= height
        bbox_width /= width
        bbox_height /= height

        label_file = os.path.splitext(file_name)[0] + ".txt"

        label_path = os.path.join(
            label_output_path,
            label_file
        )

        with open(label_path, "a") as f:
            f.write(
                f"{class_id} "
                f"{x_center} "
                f"{y_center} "
                f"{bbox_width} "
                f"{bbox_height}\n"
            )

        annotation_count += 1

    # Copy images
    for image_info in data["images"]:

        file_name = image_info["file_name"]

        source = os.path.join(
            image_input_path,
            file_name
        )

        destination = os.path.join(
            image_output_path,
            file_name
        )

        if os.path.exists(source):
            shutil.copy2(source, destination)

    print(f"{split.upper()} conversion completed!")
    print(f"Images: {len(images)}")
    print(f"Annotations: {annotation_count}")


convert_split("train")
convert_split("val")
convert_split("test")

print("\nAll conversions completed successfully!")