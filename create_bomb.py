from PIL import Image, ImageDraw

# 创建一个新的透明图片
size = 40
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 画一个黑色的圆形作为炸弹主体
center = size // 2
radius = 15
draw.ellipse([center - radius, center - radius, 
              center + radius, center + radius], 
             fill=(0, 0, 0, 255))

# 画引线（导火索）
fuse_x = center - 3
fuse_y = center - radius - 5
draw.line([center, center - radius, fuse_x, fuse_y], 
          fill=(100, 100, 100, 255), width=2)

# 画火花
draw.ellipse([fuse_x - 3, fuse_y - 3, fuse_x + 3, fuse_y + 3], 
             fill=(255, 100, 0, 255))

# 保存
img.save('assets/bomb.png')
print("黑色炸弹图片已创建！")
