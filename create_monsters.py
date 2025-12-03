from PIL import Image, ImageDraw
import random

def create_monster(filename, primary_color, secondary_color):
    """创建一个怪物图片"""
    size = 100
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 身体 - 不规则形状
    center_x, center_y = size // 2, size // 2
    body_points = []
    num_points = 8
    for i in range(num_points):
        angle = (i * 360 / num_points) * 3.14159 / 180
        radius = random.randint(30, 40)
        x = center_x + int(radius * (1 if i % 2 == 0 else 0.8) * ((i+1) % 2 * 2 - 1))
        y = center_y + int(radius * (1 if i % 2 == 1 else 0.8) * (i % 2 * 2 - 1))
        if i < 4:
            x = center_x - 35 + (i * 23)
            y = center_y - 35 + (i % 2) * 20
        else:
            x = center_x - 35 + ((i-4) * 23)
            y = center_y + 15 + ((i-4) % 2) * 20
        body_points.append((x, y))
    
    # 画身体
    draw.polygon(body_points, fill=primary_color)
    
    # 眼睛
    eye1_x, eye1_y = center_x - 15, center_y - 10
    eye2_x, eye2_y = center_x + 15, center_y - 10
    
    # 白色眼白
    draw.ellipse([eye1_x - 8, eye1_y - 8, eye1_x + 8, eye1_y + 8], fill=(255, 255, 255, 255))
    draw.ellipse([eye2_x - 8, eye2_y - 8, eye2_x + 8, eye2_y + 8], fill=(255, 255, 255, 255))
    
    # 瞳孔
    draw.ellipse([eye1_x - 4, eye1_y - 4, eye1_x + 4, eye1_y + 4], fill=(0, 0, 0, 255))
    draw.ellipse([eye2_x - 4, eye2_y - 4, eye2_x + 4, eye2_y + 4], fill=(0, 0, 0, 255))
    
    # 嘴巴 - 锯齿状
    mouth_y = center_y + 15
    mouth_points = []
    for i in range(6):
        x = center_x - 20 + i * 8
        y = mouth_y + (i % 2) * 5
        mouth_points.append((x, y))
    draw.line(mouth_points, fill=(0, 0, 0, 255), width=2)
    
    # 触角或装饰
    draw.line([center_x - 25, center_y - 35, center_x - 30, center_y - 45], fill=secondary_color, width=3)
    draw.line([center_x + 25, center_y - 35, center_x + 30, center_y - 45], fill=secondary_color, width=3)
    draw.ellipse([center_x - 33, center_y - 48, center_x - 27, center_y - 42], fill=secondary_color)
    draw.ellipse([center_x + 27, center_y - 48, center_x + 33, center_y - 42], fill=secondary_color)
    
    img.save(filename)
    print(f"怪物图片已创建: {filename}")

# 创建3种不同颜色的怪物
create_monster('assets/monster3.png', (150, 50, 200, 255), (100, 0, 150, 255))  # 紫色怪物
create_monster('assets/monster4.png', (50, 150, 50, 255), (0, 100, 0, 255))    # 绿色怪物
create_monster('assets/monster5.png', (200, 100, 50, 255), (150, 50, 0, 255))  # 橙色怪物

print("所有新怪物图片创建完成！")
