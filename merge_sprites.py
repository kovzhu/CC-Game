from PIL import Image

def merge_sprites(standing_path, running_path, output_path, cut_y=680):
    print(f"Merging {standing_path} and {running_path}...")
    try:
        standing = Image.open(standing_path).convert("RGBA")
        running = Image.open(running_path).convert("RGBA")
        
        # Create a new blank image
        merged = Image.new("RGBA", standing.size)
        
        # Paste running upper body (0 to cut_y)
        # crop box is (left, upper, right, lower)
        upper_body = running.crop((0, 0, running.width, cut_y))
        merged.paste(upper_body, (0, 0))
        
        # Paste standing lower body (cut_y to height)
        lower_body = standing.crop((0, cut_y, standing.width, standing.height))
        merged.paste(lower_body, (0, cut_y))
        
        merged.save(output_path, "PNG")
        print(f"Saved merged sprite to {output_path}")
        
    except Exception as e:
        print(f"Failed to merge sprites: {e}")

assets_dir = "/Users/chaowei/Documents/Python/CC-Game/assets"
hero1_path = f"{assets_dir}/hero1.png" # Standing (legs source)
hero2_path = f"{assets_dir}/hero2.png" # Running (torso source)

# We will overwrite hero1.png with the merged version
merge_sprites(hero1_path, hero2_path, hero1_path, cut_y=680)
