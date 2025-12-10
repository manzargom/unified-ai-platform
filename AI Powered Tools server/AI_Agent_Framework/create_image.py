# create_image.py - Run this once
from PIL import Image, ImageDraw

# Create folder if it doesn't exist
import os
os.makedirs('static/images', exist_ok=True)

# Create image
img = Image.new('RGB', (300, 200), color=(30, 30, 46))
draw = ImageDraw.Draw(img)

# Draw border
draw.rectangle([10, 10, 290, 190], outline=(255, 94, 0), width=2)

# Draw text
draw.text((80, 80), "Asset Preview", fill=(255, 94, 0))
draw.text((120, 120), "Image", fill=(255, 94, 0))

# Save
img.save('static/images/placeholder.png')
print('✅ Created: static/images/placeholder.png')
print('✅ Size: 300x200 pixels')