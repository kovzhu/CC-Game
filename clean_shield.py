from PIL import Image
import numpy as np

# 加载护盾图片
img = Image.open('assets/shield.png').convert('RGBA')
data = np.array(img)

# 创建一个新的alpha通道
# 将黑色、灰色和深色像素设为透明
red, green, blue, alpha = data.T

# 找到黑色、灰色区域 (RGB值都比较接近且较低)
dark_areas = (red < 100) & (green < 100) & (blue < 100)

# 将这些区域设为完全透明
data[..., 3][dark_areas.T] = 0

# 保存结果
img_cleaned = Image.fromarray(data)
img_cleaned.save('assets/shield.png')
print("护盾图片已清理完成！")
