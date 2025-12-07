from PIL import Image
import os

def remove_background(path):
    print(f"Processing {path}...")
    try:
        img = Image.open(path)
        img = img.convert("RGBA")
        datas = img.getdata()
        
        newData = []
        # Get the background color from top-left pixel
        bg_color = datas[0]
        # Allow some tolerance for "near white"
        tolerance = 30
        
        for item in datas:
            # Check if pixel is close to white (high R, G, B)
            if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
                newData.append((255, 255, 255, 0)) # Transparent
            else:
                newData.append(item)
        
        img.putdata(newData)
        img.save(path, "PNG")
        print(f"Saved cleaned {path}")
    except Exception as e:
        print(f"Failed to process {path}: {e}")

assets_dir = "/Users/chaowei/Documents/Python/CC-Game/assets"
for i in range(1, 4):
    path = os.path.join(assets_dir, f"hero{i}.png")
    if os.path.exists(path):
        remove_background(path)
    else:
        print(f"{path} does not exist.")
