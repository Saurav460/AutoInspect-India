from PIL import Image, ImageDraw


# ==========================================
# INPUT / OUTPUT
# ==========================================

source_image = "dataset/images/test/000042.jpg"

before_image = "before_real_test.jpg"
after_image = "after_real_test.jpg"


# ==========================================
# LOAD ORIGINAL IMAGE
# ==========================================

image = Image.open(source_image).convert("RGB")

# AFTER = original image with real CarDD damage
image.save(after_image)


# ==========================================
# CREATE BEFORE IMAGE
# ==========================================

before = image.copy()

draw = ImageDraw.Draw(before)


# ==========================================
# HIDE ONE KNOWN DENT
# ==========================================
# Ground-truth first dent from 000042.txt
#
# Normalized:
# class = 0
# x_center = 0.12484
# y_center = 0.471604
# width = 0.1106
# height = 0.234693
#
# Image size = 1000 x 667
# ==========================================

image_width = 1000
image_height = 667

x_center = 0.12484 * image_width
y_center = 0.4716041979 * image_height

box_width = 0.1106 * image_width
box_height = 0.2346926537 * image_height


x1 = int(x_center - box_width / 2)
y1 = int(y_center - box_height / 2)

x2 = int(x_center + box_width / 2)
y2 = int(y_center + box_height / 2)


# Fill the damage region using nearby neutral gray
draw.rectangle(
    [x1, y1, x2, y2],
    fill=(128, 128, 128)
)


# Save BEFORE image
before.save(before_image)


print("Controlled Before/After test created successfully.")

print("\nBEFORE:", before_image)
print("AFTER :", after_image)

print("\nHidden dent region:")
print("x1 =", x1)
print("y1 =", y1)
print("x2 =", x2)
print("y2 =", y2)