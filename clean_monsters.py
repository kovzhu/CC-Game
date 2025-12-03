from PIL import Image
import numpy as np

# 处理怪物图片1
for i in [1, 2]:
    try:
        # 加载怪物图片
        img = Image.open(f'assets/monster{i}.png').convert('RGBA')
        data = np.array(img)

        # 创建一个新的alpha通道
        red, green, blue, alpha = data.T

        # 找到白色或浅色背景区域
        white_areas = (red > 200) & (green > 200) & (blue > 200)
        
        # 找到黑色或深色背景区域
        dark_areas = (red < 50) & (green < 50) & (blue < 50)

        # 将这些区域设为透明
        data[..., 3][white_areas.T] = 0
        data[..., 3][dark_areas.T] = 0

        # 保存结果
        img_cleaned = Image.fromarray(data)
        img_cleaned.save(f'assets/monster{i}.png')
        print(f"怪物图片{i}已清理完成！")
    except Exception as e:
        print(f"处理怪物图片{i}时出错: {e}")
