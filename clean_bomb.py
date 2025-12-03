from PIL import Image
import numpy as np

# 加载炸弹图片
img = Image.open('assets/bomb.png').convert('RGBA')
data = np.array(img)

# 创建一个新的alpha通道
red, green, blue, alpha = data.T

# 找到白色或浅色背景区域
white_areas = (red > 200) & (green > 200) & (blue > 200)

# 找到灰色格子区域（灰色通常是RGB值接近且在中间范围）
gray_areas = (red > 100) & (red < 200) & \
             (green > 100) & (green < 200) & \
             (blue > 100) & (blue < 200) & \
             (abs(red - green) < 50) & (abs(green - blue) < 50)

# 找到深色背景区域
dark_bg = (red < 50) & (green < 50) & (blue < 50)

# 将这些区域设为透明
data[..., 3][white_areas.T] = 0
data[..., 3][gray_areas.T] = 0
data[..., 3][dark_bg.T] = 0

# 保存结果
img_cleaned = Image.fromarray(data)
img_cleaned.save('assets/bomb.png')
print("炸弹图片已清理完成！灰色格子已去除。")
