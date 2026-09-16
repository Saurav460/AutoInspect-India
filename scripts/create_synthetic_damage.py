from PIL import Image, ImageDraw


# Load the original image
image = Image.open("after.jpg").convert("RGB")

# Create a drawing object
draw = ImageDraw.Draw(image)

# Add an artificial red damage-like mark
draw.line(
    [(250, 300), (350, 350), (450, 320)],
    fill=(255, 0, 0),
    width=12
)

# Add another smaller mark
draw.line(
    [(300, 380), (420, 400)],
    fill=(255, 0, 0),
    width=8
)

# Save modified image
image.save("after.jpg")

print("Synthetic damage added successfully.")