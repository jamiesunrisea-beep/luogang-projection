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

PARTICLE_COUNT = 800  # 3D点云需要更多粒子
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


def generate_3d_particles(points_3d, scale=300):
    """从3D点云生成粒子"""
    particles = []
    
    # 均匀采样点云
    step = max(1, len(points_3d) // PARTICLE_COUNT)
    
    for i in range(0, len(points_3d), step):
        if len(particles) >= PARTICLE_COUNT:
            break
        
        x, y, z = points_3d[i]
        # 缩放3D坐标
        x3d = x * scale
        y3d = y * scale
        z3d = z * scale
        
        color_variant = i % 4
        particles.append(Particle3D(x3d, y3d, z3d, color_variant))
    
    # 补充粒子
    while len(particles) < PARTICLE_COUNT:
        point = random.choice(points_3d)
        x, y, z = point
        x3d = x * scale
        y3d = y * scale
        z3d = z * scale
        color_variant = random.randint(0, 3)
        particles.append(Particle3D(x3d, y3d, z3d, color_variant))
    
    return particles[:PARTICLE_COUNT]


def main():
    # 获取3D点云
    points_3d = get_airplane_3d_points()
    
    # 生成3D粒子
    particles = generate_3d_particles(points_3d, scale=200)
    
    running = True
    start_time = time.time()
    
    # 旋转角度
    angle_x = 0
    angle_y = 0
    angle_z = 0
    
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
        for p in particles:
            p.rotate(angle_x, angle_y, angle_z)
            if p.project(camera_distance=8.0):
                p.update_color(current_time)
                visible_particles.append(p)
        
        # 3. 按深度排序（从远到近绘制，避免遮挡问题）
        visible_particles.sort(key=lambda p: p.depth, reverse=True)
        
        # 4. 绘制所有可见粒子
        for p in visible_particles:
            p.draw(SCREEN)
        
        # 显示信息
        pygame.display.set_caption(f"3D无人机灯光秀 - 粒子数: {len(visible_particles)} - 按ESC退出")
        
        pygame.display.flip()
        CLOCK.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
