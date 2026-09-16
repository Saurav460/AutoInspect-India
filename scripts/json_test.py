import json


inspection_result = {
    "existing_damage": [
        {
            "type": "glass shatter",
            "confidence": 0.906,
            "iou": 0.996
        },
        {
            "type": "dent",
            "confidence": 0.738,
            "iou": 0.944
        }
    ],
    "potential_new_damage": [
        {
            "type": "dent",
            "confidence": 0.612
        }
    ],
    "overall_status": "Potential New Damage Detected"
}


print("\n===== JSON RESULT =====")

print(
    json.dumps(
        inspection_result,
        indent=4
    )
)