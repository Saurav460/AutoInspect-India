from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ultralytics import YOLO

from pathlib import Path
from datetime import datetime
import uuid
import json
import os

import cv2


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="AutoInspect India API",
    description="AI-powered vehicle damage inspection system",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "runs"
    / "detect"
    / "train-5"
    / "weights"
    / "best.pt"
)

TEMP_DIR = BASE_DIR / "temp_uploads"
REPORT_DIR = BASE_DIR / "reports"

TEMP_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


# ============================================================
# MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise RuntimeError(
        f"YOLO model not found at: {MODEL_PATH}"
    )

model = YOLO(str(MODEL_PATH))


# ============================================================
# CONSTANTS
# ============================================================

CONFIDENCE_THRESHOLD = 0.50
IOU_THRESHOLD = 0.50

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

CLASS_NAMES = [
    "dent",
    "scratch",
    "crack",
    "glass shatter",
    "lamp broken",
    "tire flat",
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def generate_inspection_id():
    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    short_id = uuid.uuid4().hex[:6].upper()

    return f"AI-{timestamp}-{short_id}"


def current_timestamp():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def validate_extension(filename):
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Use JPG, JPEG, PNG or WEBP."
            ),
        )

    return extension


def save_upload(file, inspection_id):
    extension = validate_extension(file.filename)

    unique_filename = (
        f"{inspection_id}-{uuid.uuid4().hex}"
        f"{extension}"
    )

    file_path = TEMP_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


def validate_image(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image.",
        )

    return image


def calculate_relative_area(
    x1,
    y1,
    x2,
    y2,
    image_width,
    image_height,
):
    box_area = max(0, x2 - x1) * max(0, y2 - y1)

    image_area = image_width * image_height

    if image_area == 0:
        return 0.0

    return round(
        (box_area / image_area) * 100,
        2,
    )


def estimate_severity(relative_area):
    """
    Project-level visual heuristic.

    This is NOT an insurance or industry
    standard severity classification.
    """

    if relative_area < 2:
        return "Minor"

    if relative_area <= 10:
        return "Moderate"

    return "Severe"


def get_image_location(
    center_x,
    center_y,
    image_width,
    image_height,
):
    third_width = image_width / 3
    third_height = image_height / 3

    if center_x < third_width:
        horizontal = "Left"

    elif center_x < third_width * 2:
        horizontal = "Center"

    else:
        horizontal = "Right"

    if center_y < third_height:
        vertical = "Top"

    elif center_y < third_height * 2:
        vertical = "Middle"

    else:
        vertical = "Bottom"

    return f"{vertical}-{horizontal}"


def calculate_iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    intersection_x1 = max(ax1, bx1)
    intersection_y1 = max(ay1, by1)

    intersection_x2 = min(ax2, bx2)
    intersection_y2 = min(ay2, by2)

    intersection_width = max(
        0,
        intersection_x2 - intersection_x1,
    )

    intersection_height = max(
        0,
        intersection_y2 - intersection_y1,
    )

    intersection_area = (
        intersection_width
        * intersection_height
    )

    area_a = (
        max(0, ax2 - ax1)
        * max(0, ay2 - ay1)
    )

    area_b = (
        max(0, bx2 - bx1)
        * max(0, by2 - by1)
    )

    union_area = (
        area_a
        + area_b
        - intersection_area
    )

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


# ============================================================
# YOLO DETECTION
# ============================================================

def get_detections(image_path):
    image = validate_image(image_path)

    image_height, image_width = image.shape[:2]

    results = model(
        str(image_path),
        conf=CONFIDENCE_THRESHOLD,
        verbose=False,
    )

    detections = []

    for result in results:

        if result.boxes is None:
            continue

        boxes = result.boxes

        for i in range(len(boxes)):

            confidence = float(
                boxes.conf[i].item()
            )

            class_id = int(
                boxes.cls[i].item()
            )

            x1, y1, x2, y2 = (
                boxes.xyxy[i]
                .tolist()
            )

            x1 = round(float(x1), 2)
            y1 = round(float(y1), 2)
            x2 = round(float(x2), 2)
            y2 = round(float(y2), 2)

            relative_area = (
                calculate_relative_area(
                    x1,
                    y1,
                    x2,
                    y2,
                    image_width,
                    image_height,
                )
            )

            center_x = (
                x1 + x2
            ) / 2

            center_y = (
                y1 + y2
            ) / 2

            location = get_image_location(
                center_x,
                center_y,
                image_width,
                image_height,
            )

            severity = estimate_severity(
                relative_area
            )

            if 0 <= class_id < len(CLASS_NAMES):
                damage_type = CLASS_NAMES[
                    class_id
                ]
            else:
                damage_type = "unknown"

            detections.append(
                {
                    "type": damage_type,
                    "confidence": round(
                        confidence,
                        4,
                    ),
                    "bounding_box": [
                        x1,
                        y1,
                        x2,
                        y2,
                    ],
                    "relative_area": relative_area,
                    "location": location,
                    "severity": severity,
                }
            )

    return detections


# ============================================================
# REPORT STORAGE
# ============================================================

def save_report_json(report):
    report_id = report["inspection_id"]

    report_path = (
        REPORT_DIR
        / f"{report_id}.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return report_path


# ============================================================
# PDF GENERATION
# ============================================================

def generate_pdf(report):
    from reportlab.lib import colors

    from reportlab.lib.enums import (
        TA_CENTER,
        TA_LEFT,
    )

    from reportlab.lib.pagesizes import A4

    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle,
    )

    from reportlab.lib.units import mm

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )

    report_id = report[
        "inspection_id"
    ]

    pdf_path = (
        REPORT_DIR
        / f"{report_id}.pdf"
    )

    wine = colors.HexColor(
        "#8F1D3F"
    )

    red = colors.HexColor(
        "#E63956"
    )

    dark = colors.HexColor(
        "#15131A"
    )

    light = colors.HexColor(
        "#FCE7ED"
    )

    grey = colors.HexColor(
        "#6B7280"
    )

    white = colors.white

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        textColor=dark,
        alignment=TA_LEFT,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=grey,
        spaceAfter=10,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=15,
        leading=18,
        textColor=wine,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=14,
        textColor=dark,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=grey,
    )

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="AutoInspect India Inspection Report",
    )

    story = []

    # ========================================================
    # HEADER
    # ========================================================

    story.append(
        Paragraph(
            "AutoInspect India",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "AI Vehicle Damage Inspection Report",
            subtitle_style,
        )
    )

    header_data = [
        [
            Paragraph(
                "<b>Inspection ID</b>",
                body_style,
            ),
            Paragraph(
                report_id,
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Report Type</b>",
                body_style,
            ),
            Paragraph(
                report["report_type"],
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Date & Time</b>",
                body_style,
            ),
            Paragraph(
                report["created_at"],
                body_style,
            ),
        ],
    ]

    header_table = Table(
        header_data,
        colWidths=[
            40 * mm,
            125 * mm,
        ],
    )

    header_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    light,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#E5D5DA"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.HexColor("#E5D5DA"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(header_table)

    # ========================================================
    # VEHICLE DETAILS
    # ========================================================

    vehicle = report.get(
        "vehicle",
        {},
    )

    story.append(
        Paragraph(
            "Vehicle Information",
            section_style,
        )
    )

    vehicle_data = [
        [
            Paragraph(
                "<b>Registration Number</b>",
                body_style,
            ),
            Paragraph(
                vehicle.get(
                    "vehicle_number",
                    "Not provided",
                ),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Vehicle Model</b>",
                body_style,
            ),
            Paragraph(
                vehicle.get(
                    "vehicle_model",
                    "Not provided",
                ),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Customer / Driver</b>",
                body_style,
            ),
            Paragraph(
                vehicle.get(
                    "customer_name",
                    "Not provided",
                ),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Inspector</b>",
                body_style,
            ),
            Paragraph(
                vehicle.get(
                    "inspector_name",
                    "Not provided",
                ),
                body_style,
            ),
        ],
    ]

    vehicle_table = Table(
        vehicle_data,
        colWidths=[
            55 * mm,
            110 * mm,
        ],
    )

    vehicle_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F8F6F7"
                    ),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#E7DFE3"
                    ),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.HexColor(
                        "#E7DFE3"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(vehicle_table)

    # ========================================================
    # INSPECTION REPORT
    # ========================================================

    if report["report_type"] == "Single Image Inspection":

        result = report["result"]

        story.append(
            Paragraph(
                "Inspection Summary",
                section_style,
            )
        )

        summary_data = [
            [
                Paragraph(
                    "<b>Status</b>",
                    body_style,
                ),
                Paragraph(
                    result["status"],
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Total Damage</b>",
                    body_style,
                ),
                Paragraph(
                    str(
                        result[
                            "detection_count"
                        ]
                    ),
                    body_style,
                ),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                55 * mm,
                110 * mm,
            ],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        light,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#E7DFE3"
                        ),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.25,
                        colors.HexColor(
                            "#E7DFE3"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(
            summary_table
        )

        story.append(
            Paragraph(
                "Detected Damage",
                section_style,
            )
        )

        detections = result.get(
            "detections",
            [],
        )

        if not detections:

            story.append(
                Paragraph(
                    "No visible damage was detected above the configured confidence threshold.",
                    body_style,
                )
            )

        else:

            damage_data = [
                [
                    "Type",
                    "Confidence",
                    "Severity",
                    "Location",
                    "Area",
                ]
            ]

            for damage in detections:

                damage_data.append(
                    [
                        damage["type"].title(),
                        f'{damage["confidence"] * 100:.1f}%',
                        damage["severity"],
                        damage["location"],
                        f'{damage["relative_area"]}%',
                    ]
                )

            damage_table = Table(
                damage_data,
                colWidths=[
                    37 * mm,
                    28 * mm,
                    29 * mm,
                    36 * mm,
                    25 * mm,
                ],
                repeatRows=1,
            )

            damage_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            wine,
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            white,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.35,
                            colors.HexColor(
                                "#DDCCD2"
                            ),
                        ),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [
                                white,
                                colors.HexColor(
                                    "#FCF8FA"
                                ),
                            ],
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE",
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(
                damage_table
            )

    # ========================================================
    # COMPARISON REPORT
    # ========================================================

    else:

        result = report["result"]

        story.append(
            Paragraph(
                "Comparison Summary",
                section_style,
            )
        )

        comparison_summary = [
            [
                Paragraph(
                    "<b>Overall Status</b>",
                    body_style,
                ),
                Paragraph(
                    result[
                        "summary"
                    ]["overall_status"],
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Existing Damage</b>",
                    body_style,
                ),
                Paragraph(
                    str(
                        result[
                            "summary"
                        ][
                            "existing_damage_count"
                        ]
                    ),
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Potential New Damage</b>",
                    body_style,
                ),
                Paragraph(
                    str(
                        result[
                            "summary"
                        ][
                            "potential_new_damage_count"
                        ]
                    ),
                    body_style,
                ),
            ],
        ]

        comparison_table = Table(
            comparison_summary,
            colWidths=[
                55 * mm,
                110 * mm,
            ],
        )

        comparison_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        light,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#E7DFE3"
                        ),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.25,
                        colors.HexColor(
                            "#E7DFE3"
                        ),
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(
            comparison_table
        )

        # ----------------------------------------------------
        # EXISTING DAMAGE
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "Existing Damage",
                section_style,
            )
        )

        existing_damage = result.get(
            "existing_damage",
            [],
        )

        if not existing_damage:

            story.append(
                Paragraph(
                    "No existing damage matches were found.",
                    body_style,
                )
            )

        else:

            existing_data = [
                [
                    "Type",
                    "Confidence",
                    "IoU",
                    "Severity",
                    "Location",
                ]
            ]

            for damage in existing_damage:

                existing_data.append(
                    [
                        damage["type"].title(),
                        f'{damage["confidence"] * 100:.1f}%',
                        str(damage["iou"]),
                        damage["severity"],
                        damage["location"],
                    ]
                )

            existing_table = Table(
                existing_data,
                colWidths=[
                    37 * mm,
                    29 * mm,
                    22 * mm,
                    31 * mm,
                    36 * mm,
                ],
                repeatRows=1,
            )

            existing_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            wine,
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            white,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.35,
                            colors.HexColor(
                                "#DDCCD2"
                            ),
                        ),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [
                                white,
                                colors.HexColor(
                                    "#FCF8FA"
                                ),
                            ],
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(
                existing_table
            )

        # ----------------------------------------------------
        # NEW DAMAGE
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "Potential New Damage",
                section_style,
            )
        )

        new_damage = result.get(
            "potential_new_damage",
            [],
        )

        if not new_damage:

            story.append(
                Paragraph(
                    "No potential new damage was detected.",
                    body_style,
                )
            )

        else:

            new_data = [
                [
                    "Type",
                    "Confidence",
                    "Severity",
                    "Location",
                    "Area",
                ]
            ]

            for damage in new_damage:

                new_data.append(
                    [
                        damage["type"].title(),
                        f'{damage["confidence"] * 100:.1f}%',
                        damage["severity"],
                        damage["location"],
                        f'{damage["relative_area"]}%',
                    ]
                )

            new_table = Table(
                new_data,
                colWidths=[
                    37 * mm,
                    29 * mm,
                    31 * mm,
                    36 * mm,
                    25 * mm,
                ],
                repeatRows=1,
            )

            new_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            red,
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            white,
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.35,
                            colors.HexColor(
                                "#E8CCD3"
                            ),
                        ),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [
                                colors.HexColor(
                                    "#FFF7F9"
                                ),
                                white,
                            ],
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            5,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6,
                        ),
                    ]
                )
            )

            story.append(
                new_table
            )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    story.append(
        Spacer(1, 15)
    )

    disclaimer = (
        "<b>Important:</b> This report contains "
        "AI-generated visual inspection results. "
        "Severity is based on a project-level "
        "visual heuristic and is not an insurance, "
        "legal, mechanical, or industry-standard "
        "assessment. Potential new damage should "
        "be manually verified."
    )

    story.append(
        Paragraph(
            disclaimer,
            small_style,
        )
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            "Generated by AutoInspect India",
            small_style,
        )
    )

    doc.build(story)

    return pdf_path


# ============================================================
# HOME
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AutoInspect India API is running!",
        "model": "YOLO",
        "version": "1.0.0",
    }


# ============================================================
# INSPECT
# ============================================================

@app.post("/inspect")
async def inspect(
    file: UploadFile = File(...),

    vehicle_number: str = Form(""),
    vehicle_model: str = Form(""),
    customer_name: str = Form(""),
    inspector_name: str = Form(""),
):
    inspection_id = generate_inspection_id()

    image_path = None

    try:

        image_path = save_upload(
            file,
            inspection_id,
        )

        detections = get_detections(
            image_path
        )

        status = (
            "Damage Detected"
            if detections
            else "No Visible Damage Detected"
        )

        result = {
            "filename": file.filename,

            "detections": detections,

            "detection_count": len(
                detections
            ),

            "status": status,
        }

        report = {
            "inspection_id": inspection_id,

            "created_at": current_timestamp(),

            "report_type":
                "Single Image Inspection",

            "vehicle": {
                "vehicle_number":
                    vehicle_number.strip(),

                "vehicle_model":
                    vehicle_model.strip(),

                "customer_name":
                    customer_name.strip(),

                "inspector_name":
                    inspector_name.strip(),
            },

            "result": result,
        }

        save_report_json(report)

        return {
            **result,

            "inspection_id":
                inspection_id,

            "created_at":
                report["created_at"],

            "vehicle":
                report["vehicle"],
        }

    finally:

        if image_path and image_path.exists():
            image_path.unlink(
                missing_ok=True
            )


# ============================================================
# COMPARE
# ============================================================

@app.post("/compare")
async def compare(
    before_image: UploadFile = File(...),
    after_image: UploadFile = File(...),

    vehicle_number: str = Form(""),
    vehicle_model: str = Form(""),
    customer_name: str = Form(""),
    inspector_name: str = Form(""),
):
    inspection_id = generate_inspection_id()

    before_path = None
    after_path = None

    try:

        before_path = save_upload(
            before_image,
            inspection_id,
        )

        after_path = save_upload(
            after_image,
            inspection_id,
        )

        before_detections = get_detections(
            before_path
        )

        after_detections = get_detections(
            after_path
        )

        used_before_indices = set()

        existing_damage = []

        potential_new_damage = []

        # ----------------------------------------------------
        # Match AFTER detections to BEFORE detections
        # ----------------------------------------------------

        for after_damage in after_detections:

            best_match_index = None
            best_iou = 0.0

            for i, before_damage in enumerate(
                before_detections
            ):

                if i in used_before_indices:
                    continue

                if (
                    before_damage["type"]
                    != after_damage["type"]
                ):
                    continue

                iou = calculate_iou(
                    before_damage[
                        "bounding_box"
                    ],
                    after_damage[
                        "bounding_box"
                    ],
                )

                if iou > best_iou:
                    best_iou = iou
                    best_match_index = i

            if (
                best_match_index is not None
                and best_iou >= IOU_THRESHOLD
            ):

                used_before_indices.add(
                    best_match_index
                )

                existing_damage.append(
                    {
                        "type":
                            after_damage[
                                "type"
                            ],

                        "confidence":
                            after_damage[
                                "confidence"
                            ],

                        "iou":
                            round(
                                best_iou,
                                4,
                            ),

                        "relative_area":
                            after_damage[
                                "relative_area"
                            ],

                        "location":
                            after_damage[
                                "location"
                            ],

                        "severity":
                            after_damage[
                                "severity"
                            ],
                    }
                )

            else:

                potential_new_damage.append(
                    {
                        "type":
                            after_damage[
                                "type"
                            ],

                        "confidence":
                            after_damage[
                                "confidence"
                            ],

                        "bounding_box":
                            after_damage[
                                "bounding_box"
                            ],

                        "relative_area":
                            after_damage[
                                "relative_area"
                            ],

                        "location":
                            after_damage[
                                "location"
                            ],

                        "severity":
                            after_damage[
                                "severity"
                            ],
                    }
                )

        overall_status = (
            "Potential New Damage Detected"
            if potential_new_damage
            else "No Potential New Damage Detected"
        )

        result = {
            "before_filename":
                before_image.filename,

            "after_filename":
                after_image.filename,

            "existing_damage":
                existing_damage,

            "potential_new_damage":
                potential_new_damage,

            "summary": {
                "existing_damage_count":
                    len(existing_damage),

                "potential_new_damage_count":
                    len(
                        potential_new_damage
                    ),

                "overall_status":
                    overall_status,
            },
        }

        report = {
            "inspection_id":
                inspection_id,

            "created_at":
                current_timestamp(),

            "report_type":
                "Before / After Comparison",

            "vehicle": {
                "vehicle_number":
                    vehicle_number.strip(),

                "vehicle_model":
                    vehicle_model.strip(),

                "customer_name":
                    customer_name.strip(),

                "inspector_name":
                    inspector_name.strip(),
            },

            "result": result,
        }

        save_report_json(report)

        return {
            **result,

            "inspection_id":
                inspection_id,

            "created_at":
                report["created_at"],

            "vehicle":
                report["vehicle"],
        }

    finally:

        if before_path and before_path.exists():
            before_path.unlink(
                missing_ok=True
            )

        if after_path and after_path.exists():
            after_path.unlink(
                missing_ok=True
            )


# ============================================================
# DOWNLOAD JSON REPORT
# ============================================================

@app.get(
    "/reports/{inspection_id}/json"
)
def download_json_report(
    inspection_id: str
):

    report_path = (
        REPORT_DIR
        / f"{inspection_id}.json"
    )

    if not report_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return FileResponse(
        path=str(report_path),

        media_type="application/json",

        filename=(
            f"AutoInspect-{inspection_id}.json"
        ),
    )


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================

@app.get(
    "/reports/{inspection_id}/pdf"
)
def download_pdf_report(
    inspection_id: str
):

    report_path = (
        REPORT_DIR
        / f"{inspection_id}.json"
    )

    if not report_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    with open(
        report_path,
        "r",
        encoding="utf-8",
    ) as file:

        report = json.load(file)

    pdf_path = generate_pdf(report)

    return FileResponse(
        path=str(pdf_path),

        media_type="application/pdf",

        filename=(
            f"AutoInspect-{inspection_id}.pdf"
        ),
    )

# ============================================================
#  INSPECTION HISTORY
# ============================================================

@app.get("/reports")
def list_reports(search: str = ""):
    """
    Return all saved inspection reports.

    Optional search:
    - vehicle registration number
    - vehicle model
    - customer name
    - inspection ID
    """

    reports = []

    search = search.strip().lower()

    for report_path in REPORT_DIR.glob("*.json"):

        try:

            with open(
                report_path,
                "r",
                encoding="utf-8",
            ) as file:

                report = json.load(file)

            inspection_id = report.get(
                "inspection_id",
                "",
            )

            created_at = report.get(
                "created_at",
                "",
            )

            report_type = report.get(
                "report_type",
                "",
            )

            vehicle = report.get(
                "vehicle",
                {},
            )

            vehicle_number = vehicle.get(
                "vehicle_number",
                "",
            )

            vehicle_model = vehicle.get(
                "vehicle_model",
                "",
            )

            customer_name = vehicle.get(
                "customer_name",
                "",
            )

            result = report.get(
                "result",
                {},
            )

            if report_type == "Single Image Inspection":

                damage_count = result.get(
                    "detection_count",
                    0,
                )

                existing_damage_count = 0

                new_damage_count = 0

                status = result.get(
                    "status",
                    "Unknown",
                )

            else:

                summary = result.get(
                    "summary",
                    {},
                )

                existing_damage_count = (
                    summary.get(
                        "existing_damage_count",
                        0,
                    )
                )

                new_damage_count = (
                    summary.get(
                        "potential_new_damage_count",
                        0,
                    )
                )

                damage_count = (
                    existing_damage_count
                    + new_damage_count
                )

                status = summary.get(
                    "overall_status",
                    "Unknown",
                )

            # ----------------------------------------------
            # SEARCH
            # ----------------------------------------------

            search_text = " ".join(
                [
                    inspection_id,
                    report_type,
                    vehicle_number,
                    vehicle_model,
                    customer_name,
                    status,
                ]
            ).lower()

            if search and search not in search_text:
                continue

            reports.append(
                {
                    "inspection_id":
                        inspection_id,

                    "created_at":
                        created_at,

                    "report_type":
                        report_type,

                    "vehicle_number":
                        vehicle_number,

                    "vehicle_model":
                        vehicle_model,

                    "customer_name":
                        customer_name,

                    "damage_count":
                        damage_count,

                    "existing_damage_count":
                        existing_damage_count,

                    "new_damage_count":
                        new_damage_count,

                    "status":
                        status,
                }
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            # Skip corrupted/unreadable report files
            continue

    # Newest report first
    reports.sort(
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    return {
        "count": len(reports),
        "reports": reports,
    }


# ============================================================
#   GET SINGLE REPORT
# ============================================================

@app.get(
    "/reports/{inspection_id}"
)
def get_report(
    inspection_id: str,
):
    """
    Return complete report JSON
    for a specific inspection ID.
    """

    report_path = (
        REPORT_DIR
        / f"{inspection_id}.json"
    )

    if not report_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Inspection report not found.",
        )

    try:

        with open(
            report_path,
            "r",
            encoding="utf-8",
        ) as file:

            report = json.load(file)

        return report

    except (
        json.JSONDecodeError,
        OSError,
    ):

        raise HTTPException(
            status_code=500,
            detail="Unable to read inspection report.",
        )    

# ============================================================
#  DELETE REPORT
# ============================================================

@app.delete("/reports/{inspection_id}")
def delete_report(
    inspection_id: str,
):
    """
    Delete a saved inspection report.

    Removes:
    - JSON report
    - Generated PDF report
    """

    json_path = (
        REPORT_DIR
        / f"{inspection_id}.json"
    )

    pdf_path = (
        REPORT_DIR
        / f"{inspection_id}.pdf"
    )

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Inspection report not found.",
        )

    try:
        # Delete JSON
        json_path.unlink(
            missing_ok=True
        )

        # Delete PDF if it exists
        pdf_path.unlink(
            missing_ok=True
        )

        return {
            "message": "Inspection report deleted successfully.",
            "inspection_id": inspection_id,
        }

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to delete report: {error}",
        )    