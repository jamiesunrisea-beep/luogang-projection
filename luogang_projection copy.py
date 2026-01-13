import pygame
import random
import math
import time

# --- 1. 初始化与参数配置 ---
pygame.init()

# 屏幕与性能设置
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("合肥骆岗公园沉浸式建筑光影装置 - 三幕投影")
CLOCK = pygame.time.Clock()

# --- 2. 颜色配置 ---
# 第一幕：远航（冷蓝色系，金属质感）
COLOR_RADAR_BLUE = (0, 100, 200)  # 雷达蓝色
COLOR_METAL_SILVER = (180, 190, 200)  # 金属银色
COLOR_SIGNAL_CYAN = (100, 200, 255)  # 信号青色
COLOR_BG_DARK = (5, 10, 25)  # 深蓝背景

# 第二幕：共生（绿色系，有机形态）
COLOR_GREEN_DARK = (20, 80, 40)  # 深绿
COLOR_GREEN_LIGHT = (50, 200, 100)  # 浅绿
COLOR_GREEN_NEON = (100, 255, 150)  # 霓虹绿
COLOR_BG_NIGHT = (10, 20, 15)  # 夜绿背景

# 第三幕：脉动（高饱和度，数据流）
COLOR_DATA_CYAN = (0, 255, 255)  # 数据青色
COLOR_DATA_BLUE = (100, 150, 255)  # 数据蓝色
COLOR_DATA_PURPLE = (200, 100, 255)  # 数据紫色
COLOR_BG_PULSE = (5, 5, 15)  # 脉动背景

FADE_ALPHA = 20

# 创建背景遮罩实现长曝光拖尾
FADE_SURFACE = pygame.Surface((WIDTH, HEIGHT))


# --- 3. 场景管理 ---
class SceneManager:
    def __init__(self):
        self.current_scene = 0
        self.scene_duration = 15.0  # 每个场景15秒（缩短时间便于测试）
        self.scene_start_time = 0.0
    
    def update(self, current_time):
        if self.scene_start_time == 0.0:
            self.scene_start_time = current_time
        
        scene_time = current_time - self.scene_start_time
        if scene_time >= self.scene_duration:
            self.current_scene = (self.current_scene + 1) % 3
            self.scene_start_time = current_time
            scene_time = 0.0
        return self.current_scene, scene_time


# --- 4. 第一幕：远航（飞机仰角形态，雷达信号）---
def generate_radar_lines(particles, current_time):
    """生成雷达扫描线和矢量线条"""
    new_particles = []
    
    # 雷达扫描线（从中心向外）
    for i in range(20):
        angle = current_time * 0.5 + i * math.pi * 2 / 20
        for r in range(50, WIDTH // 2, 30):
            x = WIDTH / 2 + math.cos(angle) * r
            y = HEIGHT / 2 + math.sin(angle) * r
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                new_particles.append({
                    'x': x, 'y': y, 'size': 2,
                    'color': COLOR_RADAR_BLUE,
                    'alpha': int(150 * (1 - r / (WIDTH // 2)))
                })
    
    # 矢量网格线（航路图风格）
    for i in range(0, WIDTH, 80):
        for j in range(0, HEIGHT, 60):
            x = i + (j % 120) * 0.3
            y = j
            if 0 <= x < WIDTH:
                new_particles.append({
                    'x': x, 'y': y, 'size': 1,
                    'color': COLOR_METAL_SILVER,
                    'alpha': 80
                })
    
    return new_particles


# --- 5. 第二幕：共生（分形算法生成绿色脉络）---
def generate_fractal_branches(particles, scene_time):
    """使用分形算法生成向上攀爬的绿色脉络（完整连接的树形）"""
    new_particles = []
    
    # 信标塔中心位置
    tower_x = WIDTH / 2
    tower_base_y = HEIGHT * 0.95
    tower_height = HEIGHT * 0.85
    
    # 分形分支算法（L-System简化版）
    def generate_branch(start_x, start_y, angle, length, depth, branch_angle, particles_list):
        if depth <= 0 or length < 3:
            return
        
        # 当前分支
        end_x = start_x + math.cos(angle) * length
        end_y = start_y + math.sin(angle) * length
        
        # 绘制分支线条（更密集的点）
        steps = max(3, int(length / 2))
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # 颜色从深绿到浅绿（向上渐变）
            green_base = 50 + depth * 40
            green_intensity = int(green_base + (255 - green_base) * t)
            color = (20, min(255, green_intensity), min(255, green_intensity // 2 + 50))
            
            particles_list.append({
                'x': x, 'y': y, 'size': 2 + depth * 0.5,
                'color': color,
                'alpha': 150 + depth * 30
            })
        
        # 递归生成子分支
        if depth > 0:
            new_length = length * 0.65
            # 左分支
            generate_branch(end_x, end_y, angle - branch_angle, new_length, depth - 1, branch_angle, particles_list)
            # 右分支
            generate_branch(end_x, end_y, angle + branch_angle, new_length, depth - 1, branch_angle, particles_list)
            # 继续向上（主分支）
            if depth > 1:
                generate_branch(end_x, end_y, angle, new_length * 0.9, depth - 1, branch_angle * 0.85, particles_list)
    
    # 从底部中心生成主树干，然后分支
    growth_progress = min(1.0, scene_time / 8.0)  # 8秒内完全生长
    
    # 主树干（从底部中心向上）
    trunk_height = tower_height * growth_progress
    trunk_steps = int(trunk_height / 4)
    for i in range(trunk_steps):
        y = tower_base_y - i * 4
        x = tower_x + math.sin(scene_time * 0.5 + i * 0.1) * 5  # 轻微摆动
        color_intensity = int(50 + i / trunk_steps * 100)
        new_particles.append({
            'x': x, 'y': y, 'size': 4 - i / trunk_steps * 2,
            'color': (20, min(255, color_intensity), min(255, color_intensity // 2)),
            'alpha': 200
        })
    
    # 从主树干顶部开始分支
    trunk_top_y = tower_base_y - trunk_height
    
    # 生成多个主分支（从树干顶部向四周展开）
    num_main_branches = 6
    for i in range(num_main_branches):
        branch_angle_offset = (i / num_main_branches) * math.pi * 2
        base_angle = math.pi / 2 - 0.2 + math.sin(branch_angle_offset) * 0.4  # 主要向上，略微分散
        
        branch_length = trunk_height * (0.4 + random.random() * 0.3) * growth_progress
        
        generate_branch(
            tower_x,
            trunk_top_y,
            base_angle,
            branch_length,
            5,  # 分形深度
            math.pi / 5,  # 分支角度
            new_particles
        )
    
    return new_particles


def generate_organic_particles(particles, scene_time):
    """生成有机形态的粒子（从工业向有机转变）"""
    new_particles = []
    
    # 过渡效果：从蓝色向绿色转变
    transition = min(1.0, scene_time / 5.0)  # 5秒过渡
    
    # 生成流动的有机粒子
    for i in range(200):
        x = WIDTH / 2 + (random.random() - 0.5) * WIDTH * 0.8
        y = HEIGHT * 0.2 + random.random() * HEIGHT * 0.6
        
        # 流动效果
        wave_x = math.sin(scene_time * 2 + x * 0.01) * 20
        wave_y = math.cos(scene_time * 1.5 + y * 0.01) * 15
        x += wave_x
        y += wave_y
        
        # 颜色过渡
        r = int(COLOR_RADAR_BLUE[0] * (1 - transition) + COLOR_GREEN_LIGHT[0] * transition)
        g = int(COLOR_RADAR_BLUE[1] * (1 - transition) + COLOR_GREEN_LIGHT[1] * transition)
        b = int(COLOR_RADAR_BLUE[2] * (1 - transition) + COLOR_GREEN_LIGHT[2] * transition)
        
        new_particles.append({
            'x': x, 'y': y, 'size': 2 + random.random() * 3,
            'color': (r, g, b),
            'alpha': int(100 + 100 * transition)
        })
    
    return new_particles


# --- 6. 第三幕：脉动（实时数据流，光斑起伏）---
def generate_data_stream(particles, scene_time, mouse_pos=None):
    """生成实时数据流效果"""
    new_particles = []
    
    # 模拟数据流（垂直流动，更密集）
    stream_count = 50  # 增加数据流数量
    for i in range(stream_count):
        x = WIDTH / stream_count * i + WIDTH / (stream_count * 2)
        
        # 数据流速度（不同速度创造流动感）
        speed = 1.5 + (i % 5) * 0.5
        y_offset = (scene_time * speed * 40) % (HEIGHT + 200) - 100
        
        # 生成数据点（每个流更多的点）
        point_count = 15
        for j in range(point_count):
            y = y_offset - j * 30
            
            if -10 <= y < HEIGHT + 10:
                # 颜色变化（高频闪烁）
                color_phase = (scene_time * 6 + i * 0.5 + j * 0.3) % (math.pi * 2)
                brightness = 0.4 + 0.6 * math.sin(color_phase)
                
                # 随机选择数据流颜色
                color_variant = (i + int(scene_time * 2)) % 3
                if color_variant == 0:
                    base_color = COLOR_DATA_CYAN
                elif color_variant == 1:
                    base_color = COLOR_DATA_BLUE
                else:
                    base_color = COLOR_DATA_PURPLE
                
                r = int(base_color[0] * brightness)
                g = int(base_color[1] * brightness)
                b = int(base_color[2] * brightness)
                
                new_particles.append({
                    'x': x + (random.random() - 0.5) * 25, 'y': y,
                    'size': 2 + random.random() * 3,
                    'color': (r, g, b),
                    'alpha': int(180 * brightness)
                })
    
    # 光斑效果（模拟人流量响应）
    if mouse_pos:
        mx, my = mouse_pos
        # 在鼠标位置生成光斑
        for i in range(80):  # 增加光斑粒子数
            angle = i / 80 * math.pi * 2
            radius = 40 + random.random() * 80
            x = mx + math.cos(angle) * radius
            y = my + math.sin(angle) * radius
            
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                pulse = math.sin(scene_time * 4 + angle) * 0.5 + 0.5
                new_particles.append({
                    'x': x, 'y': y, 'size': 3 + pulse * 5,
                    'color': COLOR_DATA_PURPLE,
                    'alpha': int(220 * pulse)
                })
    
    return new_particles


def generate_pulse_particles(particles, scene_time):
    """生成脉动粒子场（背景粒子）"""
    new_particles = []
    
    # 生成随机分布的粒子（增加数量）
    for i in range(500):
        x = random.random() * WIDTH
        y = random.random() * HEIGHT
        
        # 脉动效果
        pulse_phase = scene_time * 2.5 + x * 0.01 + y * 0.01
        pulse = math.sin(pulse_phase) * 0.5 + 0.5
        size = 1.5 + pulse * 4
        
        # 颜色变化（多色混合）
        color_phase = (scene_time * 4 + i * 0.1) % (math.pi * 2)
        brightness = 0.3 + 0.7 * math.sin(color_phase)
        
        # 颜色变体
        color_variant = (i + int(scene_time)) % 3
        if color_variant == 0:
            base_color = COLOR_DATA_CYAN
        elif color_variant == 1:
            base_color = COLOR_DATA_BLUE
        else:
            base_color = COLOR_DATA_PURPLE
        
        r = int(base_color[0] * brightness)
        g = int(base_color[1] * brightness)
        b = int(base_color[2] * brightness)
        
        new_particles.append({
            'x': x, 'y': y, 'size': size,
            'color': (r, g, b),
            'alpha': int(120 * brightness * pulse)
        })
    
    return new_particles


# --- 7. 主循环 ---
def main():
    scene_manager = SceneManager()
    running = True
    start_time = time.time()
    
    # 模拟鼠标位置（可以改为真实鼠标输入）
    mouse_pos = (WIDTH / 2, HEIGHT / 2)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 空格键切换场景（用于测试）
                    scene_manager.current_scene = (scene_manager.current_scene + 1) % 3
                    scene_manager.scene_start_time = current_time
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
        
        current_time = time.time() - start_time
        scene_num, scene_time = scene_manager.update(current_time)
        
        # 根据当前场景设置背景
        if scene_num == 0:
            FADE_SURFACE.fill(COLOR_BG_DARK)
            scene_name = "第一幕：远航 (1977)"
        elif scene_num == 1:
            FADE_SURFACE.fill(COLOR_BG_NIGHT)
            scene_name = "第二幕：共生"
        else:
            FADE_SURFACE.fill(COLOR_BG_PULSE)
            scene_name = "第三幕：脉动"
        
        FADE_SURFACE.set_alpha(FADE_ALPHA)
        SCREEN.blit(FADE_SURFACE, (0, 0))
        
        # 渲染当前场景
        all_particles = []
        
        if scene_num == 0:  # 第一幕：远航
            all_particles.extend(generate_radar_lines([], scene_time))
            
        elif scene_num == 1:  # 第二幕：共生
            all_particles.extend(generate_fractal_branches([], scene_time))
            all_particles.extend(generate_organic_particles([], scene_time))
            
        else:  # 第三幕：脉动
            all_particles.extend(generate_data_stream([], scene_time, mouse_pos))
            all_particles.extend(generate_pulse_particles([], scene_time))
        
        # 绘制所有粒子
        for p in all_particles:
            if 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                # 创建半透明表面
                particle_surface = pygame.Surface((int(p['size'] * 3), int(p['size'] * 3)), pygame.SRCALPHA)
                color_with_alpha = (*p['color'], p.get('alpha', 255))
                pygame.draw.circle(particle_surface, color_with_alpha,
                                 (int(p['size'] * 1.5), int(p['size'] * 1.5)),
                                 int(p['size']))
                SCREEN.blit(particle_surface,
                           (int(p['x'] - p['size'] * 1.5), int(p['y'] - p['size'] * 1.5)),
                           special_flags=pygame.BLEND_ADD)
        
        # 显示场景信息
        pygame.display.set_caption(f"{scene_name} | 场景 {scene_num + 1}/3 | 时间: {int(scene_time)}s | 按ESC退出")
        
        pygame.display.flip()
        CLOCK.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
