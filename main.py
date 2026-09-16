from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime
from typing import Optional
from uuid import uuid4
import json
import os
import shutil

from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AutoInspect India API",
    description="AI Car Damage Detection and Inspection API",
    version="1.0.0",
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://autoinspect-india.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

TEMP_DIR = BASE_DIR / "temp_uploads"
REPORT_DIR = BASE_DIR / "reports"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# MODEL
# =========================================================

MODEL_CACHE_DIR = BASE_DIR / ".model_cache"
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_CACHE_DIR / "best.pt"

HF_REPO_ID = "Saurav460/AutoInspect-India-model"
HF_FILENAME = "best.pt"

CLASS_NAMES = [
    "dent",
    "scratch",
    "crack",
    "glass shatter",
    "lamp broken",
    "tire flat",
]

CONFIDENCE_THRESHOLD = 0.50
COMPARE_IOU_THRESHOLD = 0.50

# =========================================================
# DOWNLOAD MODEL FROM HUGGING FACE
# =========================================================

if not MODEL_FILE.exists():
    downloaded_model = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=HF_FILENAME,
        local_dir=str(MODEL_CACHE_DIR),
    )

    downloaded_path = Path(downloaded_model)

    if downloaded_path.exists() and downloaded_path != MODEL_FILE:
        shutil.copy2(downloaded_path, MODEL_FILE)

# =========================================================
# LOAD MODEL ONCE
# =========================================================

model = YOLO(str(MODEL_FILE))

# =========================================================
# HELPERS
# =========================================================


def generate_inspection_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_part = uuid4().hex[:6].upper()
    return f"AI-{timestamp}-{random_part}"


def get_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def calculate_bbox_area_percent(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    image_width: float,
    image_height: float,
) -> float:
    if image_width <= 0 or image_height <= 0:
        return 0.0

    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)

    area = width * height
    image_area = image_width * image_height

    if image_area <= 0:
        return 0.0

    return (area / image_area) * 100.0


def get_severity(area_percent: float) -> str:
    """
    Project-level visual severity heuristic.

    < 2%      -> Minor
    <= 10%    -> Moderate
    > 10%     -> Severe

    This is NOT an insurance/legal/mechanical industry standard.
    """
    if area_percent < 2:
        return "Minor"

    if area_percent <= 10:
        return "Moderate"

    return "Severe"


def get_location(
    x_center: float,
    y_center: float,
    image_width: float,
    image_height: float,
) -> str:

    if image_width <= 0 or image_height <= 0:
        return "Unknown"

    horizontal_ratio = x_center / image_width
    vertical_ratio = y_center / image_height

    if horizontal_ratio < 0.33:
        horizontal = "Left"
    elif horizontal_ratio < 0.66:
        horizontal = "Center"
    else:
        horizontal = "Right"

    if vertical_ratio < 0.33:
        vertical = "Top"
    elif vertical_ratio < 0.66:
        vertical = "Middle"
    else:
        vertical = "Bottom"

    return f"{vertical}-{horizontal}"


def calculate_iou(box_a, box_b) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_width = max(0.0, inter_x2 - inter_x1)
    inter_height = max(0.0, inter_y2 - inter_y1)

    intersection = inter_width * inter_height

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)

    union = area_a + area_b - intersection

    if union <= 0:
        return 0.0

    return intersection / union


def validate_extension(filename: str) -> bool:
    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    extension = Path(filename).suffix.lower()

    return extension in allowed_extensions


async def save_upload_file(upload_file: UploadFile, destination: Path):
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception:
        if destination.exists():
            destination.unlink()
        raise


def cleanup_file(path: Optional[Path]):
    if path and path.exists():
        try:
            path.unlink()
        except Exception:
            pass


def save_report(report_data: dict):
    inspection_id = report_data["inspection_id"]

    report_path = REPORT_DIR / f"{inspection_id}.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=2, ensure_ascii=False)

    return report_path


def read_report(inspection_id: str) -> dict:
    report_path = REPORT_DIR / f"{inspection_id}.json"

    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    try:
        with report_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read report: {str(exc)}",
        )


# =========================================================
# YOLO DETECTION
# =========================================================


def get_detections(image_path: Path) -> list:
    try:
        results = model.predict(
            source=str(image_path),
            conf=CONFIDENCE_THRESHOLD,
            imgsz=320,
            device="cpu",
            verbose=False,
        )

        if not results:
            return []

        result = results[0]

        detections = []

        image_height, image_width = result.orig_shape[:2]

        if result.boxes is None:
            return []

        for box in result.boxes:

            coordinates = box.xyxy[0].tolist()

            x1, y1, x2, y2 = [
                float(value) for value in coordinates
            ]

            confidence = float(box.conf[0].item())

            class_id = int(box.cls[0].item())

            if class_id < 0 or class_id >= len(CLASS_NAMES):
                class_name = f"class_{class_id}"
            else:
                class_name = CLASS_NAMES[class_id]

            width = max(0.0, x2 - x1)
            height = max(0.0, y2 - y1)

            x_center = x1 + width / 2
            y_center = y1 + height / 2

            area_percent = calculate_bbox_area_percent(
                x1,
                y1,
                x2,
                y2,
                image_width,
                image_height,
            )

            severity = get_severity(area_percent)

            location = get_location(
                x_center,
                y_center,
                image_width,
                image_height,
            )

            detection = {
                "class_id": class_id,
                "damage_type": class_name,
                "confidence": round(confidence * 100, 2),
                "bbox": [
                    round(x1, 2),
                    round(y1, 2),
                    round(x2, 2),
                    round(y2, 2),
                ],
                "area_percent": round(area_percent, 2),
                "severity": severity,
                "location": location,
                "image_width": image_width,
                "image_height": image_height,
            }

            detections.append(detection)

        return detections

    except Exception as exc:
        raise RuntimeError(
            f"YOLO inference failed: {str(exc)}"
        )


# =========================================================
# PDF GENERATION
# =========================================================


def generate_pdf(report_data: dict, pdf_path: Path):

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#8f1d3f"),
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#8f1d3f"),
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    story = []

    story.append(
        Paragraph(
            "AutoInspect India",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "AI Car Damage Inspection Report",
            subtitle_style,
        )
    )

    # -----------------------------------------------------
    # General Information
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Inspection Information",
            section_style,
        )
    )

    vehicle = report_data.get("vehicle", {})

    info_data = [
        ["Inspection ID", report_data.get("inspection_id", "N/A")],
        ["Created At", report_data.get("created_at", "N/A")],
        ["Report Type", report_data.get("report_type", "inspection")],
        ["Vehicle Number", vehicle.get("vehicle_number", "N/A")],
        ["Vehicle Model", vehicle.get("vehicle_model", "N/A")],
        ["Customer / Driver", vehicle.get("customer_name", "N/A")],
        ["Inspector", vehicle.get("inspector_name", "N/A")],
        ["Status", report_data.get("status", "N/A")],
    ]

    info_table = Table(
        info_data,
        colWidths=[1.8 * inch, 4.6 * inch],
    )

    info_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#fce7ed"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#222028"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e7dfe3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(info_table)
    story.append(Spacer(1, 18))

    # -----------------------------------------------------
    # Inspection summary
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Inspection Summary",
            section_style,
        )
    )

    summary = report_data.get("summary", {})

    summary_data = [
        [
            "Total Damage",
            str(summary.get("damage_count", 0)),
        ],
        [
            "Existing Damage",
            str(summary.get("existing_damage_count", 0)),
        ],
        [
            "Potential New Damage",
            str(summary.get("new_damage_count", 0)),
        ],
        [
            "Status",
            str(report_data.get("status", "N/A")),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3.2 * inch, 3.2 * inch],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#8f1d3f"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e7dfe3"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
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
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
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

    story.append(summary_table)

    # -----------------------------------------------------
    # Damage details
    # -----------------------------------------------------

    existing_damage = report_data.get(
        "existing_damage",
        report_data.get("results", []),
    )

    if existing_damage:

        story.append(
            Paragraph(
                "Detected Damage",
                section_style,
            )
        )

        damage_rows = [
            [
                "Damage",
                "Confidence",
                "Severity",
                "Location",
            ]
        ]

        for item in existing_damage:

            damage_rows.append(
                [
                    str(item.get("damage_type", "N/A")),
                    f'{item.get("confidence", 0)}%',
                    str(item.get("severity", "N/A")),
                    str(item.get("location", "N/A")),
                ]
            )

        damage_table = Table(
            damage_rows,
            colWidths=[
                2.0 * inch,
                1.3 * inch,
                1.3 * inch,
                1.8 * inch,
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
                        colors.HexColor("#8f1d3f"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#e7dfe3"),
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#fdf7f9"),
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
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(damage_table)

    # -----------------------------------------------------
    # Potential new damage
    # -----------------------------------------------------

    new_damage = report_data.get(
        "potential_new_damage",
        [],
    )

    if new_damage:

        story.append(
            Paragraph(
                "Potential New Damage",
                section_style,
            )
        )

        new_rows = [
            [
                "Damage",
                "Confidence",
                "Severity",
                "Location",
            ]
        ]

        for item in new_damage:

            new_rows.append(
                [
                    str(item.get("damage_type", "N/A")),
                    f'{item.get("confidence", 0)}%',
                    str(item.get("severity", "N/A")),
                    str(item.get("location", "N/A")),
                ]
            )

        new_table = Table(
            new_rows,
            colWidths=[
                2.0 * inch,
                1.3 * inch,
                1.3 * inch,
                1.8 * inch,
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
                        colors.HexColor("#c92845"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#e7dfe3"),
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#fdf7f9"),
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
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(new_table)

    # -----------------------------------------------------
    # Disclaimer
    # -----------------------------------------------------

    story.append(Spacer(1, 18))

    disclaimer = (
        "<b>Disclaimer:</b> This report is generated using AI-based "
        "visual inspection. Severity is a project-level visual heuristic "
        "and is not an insurance, legal, mechanical, or industry-standard "
        "assessment. Potential new damage should be manually verified."
    )

    story.append(
        Paragraph(
            disclaimer,
            normal_style,
        )
    )

    doc.build(story)


# =========================================================
# ROOT
# =========================================================


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AutoInspect India API",
        "version": "1.0.0",
    }


# =========================================================
# INSPECT
# =========================================================


@app.post("/inspect")
async def inspect(
    file: UploadFile = File(...),
    vehicle_number: str = Form(""),
    vehicle_model: str = Form(""),
    customer_name: str = Form(""),
    inspector_name: str = Form(""),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected",
        )

    if not validate_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format",
        )

    inspection_id = generate_inspection_id()
    created_at = get_timestamp()

    extension = Path(file.filename).suffix.lower()

    temp_path = TEMP_DIR / f"{inspection_id}{extension}"

    try:

        await save_upload_file(
            file,
            temp_path,
        )

        detections = get_detections(temp_path)

        status = (
            "Damage Detected"
            if detections
            else "No Damage Detected"
        )

        report_data = {
            "inspection_id": inspection_id,
            "created_at": created_at,
            "report_type": "inspection",
            "vehicle": {
                "vehicle_number": vehicle_number,
                "vehicle_model": vehicle_model,
                "customer_name": customer_name,
                "inspector_name": inspector_name,
            },
            "results": detections,
            "summary": {
                "damage_count": len(detections),
                "existing_damage_count": len(detections),
                "new_damage_count": 0,
            },
            "status": status,
            "disclaimer": (
                "AI-generated visual inspection. Severity is a "
                "project-level heuristic and requires manual verification."
            ),
        }

        save_report(report_data)

        return {
            "success": True,
            "inspection_id": inspection_id,
            "timestamp": created_at,
            "vehicle": report_data["vehicle"],
            "results": detections,
            "summary": report_data["summary"],
            "status": status,
        }

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Inspection failed: {str(exc)}",
        )

    finally:
        cleanup_file(temp_path)


# =========================================================
# COMPARE BEFORE / AFTER
# =========================================================


@app.post("/compare")
async def compare(
    before_image: UploadFile = File(...),
    after_image: UploadFile = File(...),
    vehicle_number: str = Form(""),
    vehicle_model: str = Form(""),
    customer_name: str = Form(""),
    inspector_name: str = Form(""),
):

    if not before_image.filename:
        raise HTTPException(
            status_code=400,
            detail="Before image is required",
        )

    if not after_image.filename:
        raise HTTPException(
            status_code=400,
            detail="After image is required",
        )

    if not validate_extension(before_image.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported before image format",
        )

    if not validate_extension(after_image.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported after image format",
        )

    inspection_id = generate_inspection_id()
    created_at = get_timestamp()

    before_extension = Path(
        before_image.filename
    ).suffix.lower()

    after_extension = Path(
        after_image.filename
    ).suffix.lower()

    before_path = (
        TEMP_DIR
        / f"{inspection_id}_before{before_extension}"
    )

    after_path = (
        TEMP_DIR
        / f"{inspection_id}_after{after_extension}"
    )

    try:

        await save_upload_file(
            before_image,
            before_path,
        )

        await save_upload_file(
            after_image,
            after_path,
        )

        before_detections = get_detections(
            before_path
        )

        after_detections = get_detections(
            after_path
        )

        matched_before = set()
        potential_new_damage = []
        existing_damage = []

        # -------------------------------------------------
        # Match after detections to before detections
        # -------------------------------------------------

        for after_index, after_item in enumerate(
            after_detections
        ):

            best_match_index = None
            best_iou = 0.0

            for before_index, before_item in enumerate(
                before_detections
            ):

                if before_index in matched_before:
                    continue

                # Only same damage class can match
                if (
                    after_item["class_id"]
                    != before_item["class_id"]
                ):
                    continue

                iou = calculate_iou(
                    after_item["bbox"],
                    before_item["bbox"],
                )

                if iou > best_iou:
                    best_iou = iou
                    best_match_index = before_index

            if (
                best_match_index is not None
                and best_iou >= COMPARE_IOU_THRESHOLD
            ):

                matched_before.add(
                    best_match_index
                )

                matched_item = dict(after_item)

                matched_item["match_type"] = "existing"
                matched_item["iou"] = round(
                    best_iou,
                    3,
                )

                existing_damage.append(
                    matched_item
                )

            else:

                new_item = dict(after_item)

                new_item["match_type"] = (
                    "potential_new"
                )

                new_item["iou"] = 0.0

                potential_new_damage.append(
                    new_item
                )

        # -------------------------------------------------
        # Add unmatched BEFORE damage as existing
        # -------------------------------------------------

        for before_index, before_item in enumerate(
            before_detections
        ):

            if before_index not in matched_before:

                existing_item = dict(before_item)

                existing_item["match_type"] = (
                    "existing_before_only"
                )

                existing_item["iou"] = 0.0

                existing_damage.append(
                    existing_item
                )

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        if potential_new_damage:
            status = "Potential New Damage Detected"
        elif existing_damage:
            status = "No New Damage Detected"
        else:
            status = "No Damage Detected"

        report_data = {
            "inspection_id": inspection_id,
            "created_at": created_at,
            "report_type": "compare",
            "vehicle": {
                "vehicle_number": vehicle_number,
                "vehicle_model": vehicle_model,
                "customer_name": customer_name,
                "inspector_name": inspector_name,
            },
            "before_results": before_detections,
            "after_results": after_detections,
            "existing_damage": existing_damage,
            "potential_new_damage": potential_new_damage,
            "summary": {
                "damage_count": len(
                    after_detections
                ),
                "existing_damage_count": len(
                    existing_damage
                ),
                "new_damage_count": len(
                    potential_new_damage
                ),
            },
            "status": status,
            "disclaimer": (
                "Potential new damage is an AI-based visual "
                "comparison and should be manually verified."
            ),
        }

        save_report(report_data)

        return {
            "success": True,
            "inspection_id": inspection_id,
            "timestamp": created_at,
            "vehicle": report_data["vehicle"],
            "existing_damage": existing_damage,
            "potential_new_damage": potential_new_damage,
            "summary": report_data["summary"],
            "status": status,
        }

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(exc)}",
        )

    finally:
        cleanup_file(before_path)
        cleanup_file(after_path)


# =========================================================
# GET REPORT JSON
# =========================================================


@app.get("/reports/{inspection_id}/json")
def download_json(
    inspection_id: str,
):

    report_path = REPORT_DIR / f"{inspection_id}.json"

    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return FileResponse(
        path=str(report_path),
        media_type="application/json",
        filename=f"{inspection_id}.json",
    )


# =========================================================
# GET REPORT PDF
# =========================================================


@app.get("/reports/{inspection_id}/pdf")
def download_pdf(
    inspection_id: str,
):

    report_data = read_report(
        inspection_id
    )

    pdf_path = (
        REPORT_DIR
        / f"{inspection_id}.pdf"
    )

    try:

        generate_pdf(
            report_data,
            pdf_path,
        )

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=f"{inspection_id}.pdf",
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(exc)}",
        )


# =========================================================
# REPORT LIST
# =========================================================


@app.get("/reports")
def list_reports(
    search: str = "",
):

    reports = []

    search_lower = search.strip().lower()

    for report_file in REPORT_DIR.glob("*.json"):

        try:

            with report_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                report = json.load(file)

            vehicle = report.get(
                "vehicle",
                {},
            )

            summary = report.get(
                "summary",
                {},
            )

            searchable_text = " ".join(
                [
                    str(
                        report.get(
                            "inspection_id",
                            "",
                        )
                    ),
                    str(
                        report.get(
                            "report_type",
                            "",
                        )
                    ),
                    str(
                        vehicle.get(
                            "vehicle_number",
                            "",
                        )
                    ),
                    str(
                        vehicle.get(
                            "vehicle_model",
                            "",
                        )
                    ),
                    str(
                        vehicle.get(
                            "customer_name",
                            "",
                        )
                    ),
                    str(
                        report.get(
                            "status",
                            "",
                        )
                    ),
                ]
            ).lower()

            if (
                search_lower
                and search_lower not in searchable_text
            ):
                continue

            reports.append(
                {
                    "inspection_id": report.get(
                        "inspection_id",
                        "",
                    ),
                    "created_at": report.get(
                        "created_at",
                        "",
                    ),
                    "report_type": report.get(
                        "report_type",
                        "",
                    ),
                    "vehicle_number": vehicle.get(
                        "vehicle_number",
                        "",
                    ),
                    "vehicle_model": vehicle.get(
                        "vehicle_model",
                        "",
                    ),
                    "customer_name": vehicle.get(
                        "customer_name",
                        "",
                    ),
                    "damage_count": summary.get(
                        "damage_count",
                        0,
                    ),
                    "existing_damage_count": summary.get(
                        "existing_damage_count",
                        0,
                    ),
                    "new_damage_count": summary.get(
                        "new_damage_count",
                        0,
                    ),
                    "status": report.get(
                        "status",
                        "",
                    ),
                }
            )

        except Exception:
            continue

    reports.sort(
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    return {
        "success": True,
        "count": len(reports),
        "reports": reports,
    }


# =========================================================
# GET SINGLE REPORT
# =========================================================


@app.get("/reports/{inspection_id}")
def get_single_report(
    inspection_id: str,
):

    report_data = read_report(
        inspection_id
    )

    return {
        "success": True,
        "report": report_data,
    }


# =========================================================
# DELETE REPORT
# =========================================================


@app.delete("/reports/{inspection_id}")
def delete_report(
    inspection_id: str,
):

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
            detail="Report not found",
        )

    try:

        json_path.unlink()

        if pdf_path.exists():
            pdf_path.unlink()

        return {
            "success": True,
            "message": (
                f"Report {inspection_id} deleted successfully"
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(exc)}",
        )