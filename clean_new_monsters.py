from PIL import Image
import numpy as np

# Process new monster images
for i in [3, 4]:
    try:
        # Load image
        img = Image.open(f'assets/monster{i}.png').convert('RGBA')
        data = np.array(img)

        # Create alpha channel
        red, green, blue, alpha = data.T

        # Find white or light background areas
        white_areas = (red > 200) & (green > 200) & (blue > 200)
        
        # Find black or dark background areas (just in case)
        dark_areas = (red < 50) & (green < 50) & (blue < 50)

        # Make these areas transparent
        data[..., 3][white_areas.T] = 0
        # data[..., 3][dark_areas.T] = 0 # Maybe don't remove dark for the new one if it has dark outlines

        # Save result
        img_cleaned = Image.fromarray(data)
        img_cleaned.save(f'assets/monster{i}.png')
        print(f"Monster image {i} cleaned!")
    except Exception as e:
        print(f"Error processing monster image {i}: {e}")
