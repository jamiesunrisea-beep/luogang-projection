import pygame
import random
import math
import time

# --- 1. 初始化与参数配置 ---
pygame.init()

# 屏幕与性能设置
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D无人机灯光秀 - 飞机粒子效果")
CLOCK = pygame.time.Clock()

# --- 2. 颜色配置 (发光效果配色) ---
COLOR_WHITE = (255, 255, 255)  # 白色光点
COLOR_BLUE = (150, 200, 255)  # 蓝色光点
COLOR_PINK = (255, 200, 255)  # 粉红色光点
COLOR_CYAN = (150, 255, 255)  # 青色光点
COLOR_BG = (5, 10, 40)  # 深蓝背景

PARTICLE_COUNT_AIRPLANE = 600  # 飞机的粒子数
PARTICLE_COUNT_TEXT = 400  # 文字的粒子数
FADE_ALPHA = 15  # 拖尾效果

# 创建背景遮罩实现长曝光拖尾
FADE_SURFACE = pygame.Surface((WIDTH, HEIGHT))
FADE_SURFACE.fill(COLOR_BG)
FADE_SURFACE.set_alpha(FADE_ALPHA)

# --- 3. 3D数学函数 ---
def rotate_x(point, angle):
    """绕X轴旋转"""
    x, y, z = point
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    new_y = y * cos_a - z * sin_a
    new_z = y * sin_a + z * cos_a
    return (x, new_y, new_z)

def rotate_y(point, angle):
    """绕Y轴旋转"""
    x, y, z = point
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    new_x = x * cos_a + z * sin_a
    new_z = -x * sin_a + z * cos_a
    return (new_x, y, new_z)

def rotate_z(point, angle):
    """绕Z轴旋转"""
    x, y, z = point
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    return (new_x, new_y, z)

def perspective_project(point, camera_distance=5.0):
    """透视投影：将3D点投影到2D屏幕"""
    x, y, z = point
    
    # 透视投影公式
    # 添加相机距离，使得z=0时投影正常
    z = z + camera_distance
    
    if z <= 0:
        return None  # 点在相机后面
    
    # 透视投影
    fov = 500  # 视野参数
    screen_x = x * fov / z + WIDTH / 2
    screen_y = y * fov / z + HEIGHT / 2
    
    # 返回2D坐标和深度值（用于排序和大小调整）
    return (screen_x, screen_y, z)

# --- 4. 飞机3D点云定义 ---
def get_airplane_3d_points():
    """定义飞机的3D点云（点云技术，类似无人机灯光秀）"""
    points = []
    
    # 从2D轮廓扩展为3D点云
    # 机头部分（圆形，增加Z轴厚度）
    for i in range(20):
        angle = math.pi * (i / 20)
        for z in [-0.03, 0, 0.03]:  # 3层深度
            x = 0.4 + math.cos(angle) * 0.08
            y = math.sin(angle) * 0.06
            points.append((x, y, z))
    
    # 机身上边缘（增加Z轴变化）
    for i in range(30):
        for z_offset in [-0.02, 0, 0.02]:
            x = 0.32 - (i / 30) * 0.92
            y = 0.06 - (i / 30) * 0.02
            z = z_offset
            points.append((x, y, z))
    
    # 垂直尾翼
    for i in range(15):
        x = -0.62 - (i / 15) * 0.05
        y = 0.06 + (i / 15) * 0.22
        for z in [-0.02, 0, 0.02]:
            points.append((x, y, z))
    
    # 垂直尾翼顶部
    points.append((-0.67, 0.28, 0))
    points.append((-0.65, 0.3, 0))
    
    # 机身下边缘
    for i in range(30):
        for z_offset in [-0.02, 0, 0.02]:
            x = -0.6 + (i / 30) * 0.92
            y = 0.04 - (i / 30) * 0.10
            z = z_offset
            points.append((x, y, z))
    
    # 机翼（3D厚度）
    # 右翼
    for i in range(25):
        x = 0.0 + (i / 25) * 0.35
        y = 0.02 - (i / 25) * 0.25
        for z in [-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15]:  # 机翼有厚度
            points.append((x, y, z))
    
    # 左翼
    for i in range(25):
        x = -0.3 - (i / 25) * 0.3
        y = 0.01 - (i / 25) * 0.22
        for z in [-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15]:
            points.append((x, y, z))
    
    # 引擎（3D圆形）
    engine_points = [
        (0.15, -0.18, 0),
        (-0.15, -0.17, 0),
    ]
    for ep in engine_points:
        for i in range(12):
            angle = 2 * math.pi * (i / 12)
            for z_offset in [-0.04, 0, 0.04]:
                x = ep[0] + math.cos(angle) * 0.04
                y = ep[1] + math.sin(angle) * 0.04
                z = ep[2] + z_offset
                points.append((x, y, z))
    
    return points


# --- 5. 文字3D点云定义 ---
def get_text_3d_points(text, letter_width=0.15, letter_height=0.3, letter_spacing=0.2, depth_layers=3):
    """生成文字的3D点云"""
    points = []
    letters = {
        'L': [
            # L的轮廓点（从左下角开始，顺时针）
            [(0, 0), (0, letter_height), (letter_width * 0.3, letter_height), 
             (letter_width * 0.3, letter_width * 0.3), (letter_width, letter_width * 0.3), (letter_width, 0)]
        ],
        'U': [
            # U的轮廓点
            [(0, letter_width * 0.3), (0, letter_height), (letter_width * 0.3, letter_height),
             (letter_width * 0.3, letter_width * 0.3), (letter_width * 0.7, letter_width * 0.3),
             (letter_width * 0.7, letter_height), (letter_width, letter_height), (letter_width, letter_width * 0.3)]
        ],
        'O': [
            # O的轮廓点（外圆）
            [(letter_width * 0.3, 0), (letter_width * 0.7, 0), (letter_width, letter_height * 0.5),
             (letter_width * 0.7, letter_height), (letter_width * 0.3, letter_height),
             (0, letter_height * 0.5), (letter_width * 0.3, 0)]
        ],
        'G': [
            # G的轮廓点
            [(letter_width * 0.3, 0), (letter_width * 0.7, 0), (letter_width, letter_height * 0.3),
             (letter_width, letter_height * 0.7), (letter_width * 0.7, letter_height),
             (letter_width * 0.3, letter_height), (0, letter_height * 0.7),
             (0, letter_height * 0.5), (letter_width * 0.5, letter_height * 0.5),
             (letter_width * 0.5, letter_height * 0.3), (letter_width * 0.3, 0)]
        ],
        'A': [
            # A的轮廓点
            [(letter_width * 0.5, letter_height), (letter_width * 0.2, letter_height * 0.3),
             (letter_width * 0.2, 0), (letter_width * 0.8, 0), (letter_width * 0.8, letter_height * 0.3),
             (letter_width * 0.5, letter_height), (letter_width * 0.35, letter_height * 0.5),
             (letter_width * 0.65, letter_height * 0.5)]
        ],
        'N': [
            # N的轮廓点
            [(0, 0), (0, letter_height), (letter_width * 0.3, letter_height),
             (letter_width * 0.7, letter_width * 0.3), (letter_width * 0.7, 0),
             (letter_width, 0), (letter_width, letter_height), (letter_width * 0.7, letter_height),
             (letter_width * 0.3, letter_width * 0.3), (letter_width * 0.3, 0)]
        ]
    }
    
    x_offset = 0
    for char in text.upper():
        if char not in letters:
            x_offset += letter_width + letter_spacing
            continue
            
        char_points = letters[char]
        
        for path in char_points:
            # 沿着路径生成点
            for i in range(len(path)):
                p1 = path[i]
                p2 = path[(i + 1) % len(path)]
                
                # 在两点之间插值生成点
                segments = 8
                for j in range(segments):
                    t = j / segments
                    x = p1[0] * (1 - t) + p2[0] * t
                    y = p1[1] * (1 - t) + p2[1] * t
                    
                    # 添加深度层（3D效果）
                    for z_offset in [-0.02, 0, 0.02]:
                        points.append((x + x_offset, y - letter_height / 2, z_offset))
        
        x_offset += letter_width + letter_spacing
    
    return points


class Particle3D:
    """3D粒子对象（类似无人机灯光秀中的每个无人机）"""
    
    def __init__(self, x3d, y3d, z3d, color_variant):
        self.x3d = x3d  # 3D坐标
        self.y3d = y3d
        self.z3d = z3d
        self.base_x3d = x3d  # 原始3D坐标（用于旋转）
        self.base_y3d = y3d
        self.base_z3d = z3d
        
        self.color_variant = color_variant
        self.phase = random.uniform(0, 2 * math.pi)
        
        # 2D投影坐标
        self.x2d = 0
        self.y2d = 0
        self.depth = 0  # 深度值（用于排序）
        self.size = 2
        
        colors = [COLOR_WHITE, COLOR_BLUE, COLOR_CYAN, COLOR_PINK]
        self.color = colors[color_variant % len(colors)]
    
    def rotate(self, angle_x, angle_y, angle_z):
        """应用3D旋转"""
        point = (self.base_x3d, self.base_y3d, self.base_z3d)
        point = rotate_x(point, angle_x)
        point = rotate_y(point, angle_y)
        point = rotate_z(point, angle_z)
        self.x3d, self.y3d, self.z3d = point
    
    def project(self, camera_distance=5.0):
        """投影到2D屏幕"""
        result = perspective_project((self.x3d, self.y3d, self.z3d), camera_distance)
        if result:
            self.x2d, self.y2d, self.depth = result
            # 根据深度调整粒子大小（近大远小）
            self.size = max(1, 4 - self.depth * 0.3)
            return True
        return False
    
    def update_color(self, current_time):
        """更新颜色（动态闪烁）"""
        colors = [COLOR_WHITE, COLOR_BLUE, COLOR_CYAN, COLOR_PINK]
        base_color = colors[self.color_variant % len(colors)]
        brightness = 0.6 + 0.4 * math.sin(current_time * 2 + self.phase)
        self.color = tuple(int(min(255, c * brightness)) for c in base_color)
    
    def draw(self, surface):
        """绘制粒子"""
        if self.depth <= 0:
            return
        
        # 绘制主光点
        pygame.draw.circle(surface, self.color, (int(self.x2d), int(self.y2d)), int(self.size))
        
        # 外发光效果（根据深度调整透明度）
        glow_alpha = int(80 * (1 - self.depth / 10))
        if glow_alpha > 0:
            glow_surface = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
            glow_color = (*self.color, glow_alpha)
            pygame.draw.circle(glow_surface, glow_color,
                              (int(self.size * 2), int(self.size * 2)),
                              int(self.size * 2))
            surface.blit(glow_surface,
                        (int(self.x2d - self.size * 2), int(self.y2d - self.size * 2)),
                        special_flags=pygame.BLEND_ADD)


def generate_3d_particles(points_3d, scale=300, max_count=600, offset_x=0, offset_y=0, offset_z=0):
    """从3D点云生成粒子"""
    particles = []
    
    # 均匀采样点云
    step = max(1, len(points_3d) // max_count)
    
    for i in range(0, len(points_3d), step):
        if len(particles) >= max_count:
            break
        
        x, y, z = points_3d[i]
        # 缩放3D坐标并应用偏移
        x3d = x * scale + offset_x
        y3d = y * scale + offset_y
        z3d = z * scale + offset_z
        
        color_variant = i % 4
        particles.append(Particle3D(x3d, y3d, z3d, color_variant))
    
    # 补充粒子
    while len(particles) < max_count:
        point = random.choice(points_3d)
        x, y, z = point
        x3d = x * scale + offset_x
        y3d = y * scale + offset_y
        z3d = z * scale + offset_z
        color_variant = random.randint(0, 3)
        particles.append(Particle3D(x3d, y3d, z3d, color_variant))
    
    return particles[:max_count]


def main():
    # 获取3D点云
    airplane_points = get_airplane_3d_points()
    text_points = get_text_3d_points("LUOGANG", letter_width=0.2, letter_height=0.35, letter_spacing=0.25)
    
    # 生成3D粒子
    # 飞机在中心，文字在上方
    airplane_particles = generate_3d_particles(
        airplane_points, scale=180, max_count=PARTICLE_COUNT_AIRPLANE,
        offset_x=0, offset_y=-150, offset_z=0
    )
    
    text_particles = generate_3d_particles(
        text_points, scale=120, max_count=PARTICLE_COUNT_TEXT,
        offset_x=-600, offset_y=200, offset_z=0  # 文字位置在飞机上方
    )
    
    # 合并所有粒子
    all_particles = airplane_particles + text_particles
    
    running = True
    start_time = time.time()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        current_time = time.time() - start_time
        
        # 自动旋转（类似无人机灯光秀的旋转展示）
        angle_y = current_time * 0.5  # 绕Y轴旋转（主要旋转）
        angle_x = math.sin(current_time * 0.3) * 0.3  # 轻微的上下摆动
        
        # 1. 渲染背景
        SCREEN.blit(FADE_SURFACE, (0, 0))
        
        # 2. 更新所有粒子（应用旋转和投影）
        visible_particles = []
        for p in all_particles:
            p.rotate(angle_x, angle_y, 0)
            if p.project(camera_distance=10.0):
                p.update_color(current_time)
                visible_particles.append(p)
        
        # 3. 按深度排序（从远到近绘制，避免遮挡问题）
        visible_particles.sort(key=lambda p: p.depth, reverse=True)
        
        # 4. 绘制所有可见粒子
        for p in visible_particles:
            p.draw(SCREEN)
        
        # 显示信息
        pygame.display.set_caption(f"3D无人机灯光秀 - LUOGANG - 粒子数: {len(visible_particles)} - 按ESC退出")
        
        pygame.display.flip()
        CLOCK.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
