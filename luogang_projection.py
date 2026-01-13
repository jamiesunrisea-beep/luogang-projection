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
# 第二幕：共生（绿色系，有机形态）
COLOR_GREEN_DARK = (20, 80, 40)  # 深绿
COLOR_GREEN_LIGHT = (50, 200, 100)  # 浅绿
COLOR_GREEN_NEON = (100, 255, 150)  # 霓虹绿
COLOR_BG_NIGHT = (10, 20, 15)  # 夜绿背景

# 第三幕：脉动（建筑光斑，微妙发光）
COLOR_WARM_GOLD = (170, 145, 120)  # 暖金色光（降低饱和度）
COLOR_COOL_CYAN = (130, 170, 200)  # 冷青色光（降低饱和度）
COLOR_BG_DARK_WARM = (20, 15, 10)  # 深棕背景

# 第二幕颜色过渡用
COLOR_RADAR_BLUE = (0, 100, 200)  # 雷达蓝色（用于过渡）

FADE_ALPHA = 20

# 创建背景遮罩实现长曝光拖尾
FADE_SURFACE = pygame.Surface((WIDTH, HEIGHT))


# --- 3. 场景管理 ---
class SceneManager:
    def __init__(self):
        self.current_scene = 0
        self.scene_duration = 4.0  # 每个场景4秒（总共12秒，三个场景）
        self.scene_start_time = 0.0
    
    def update(self, current_time):
        if self.scene_start_time == 0.0:
            self.scene_start_time = current_time
        
        scene_time = current_time - self.scene_start_time
        if scene_time >= self.scene_duration:
            self.current_scene = (self.current_scene + 1) % 2
            self.scene_start_time = current_time
            scene_time = 0.0
        return self.current_scene, scene_time


# --- 4. 第二幕：共生（分形算法生成绿色脉络）---
def generate_fractal_branches(particles, scene_time):
    """使用分形算法生成向上攀爬的绿色脉络（完整连接的树形）"""
    new_particles = []
    
    # 信标塔中心位置
    tower_x = WIDTH / 2
    tower_base_y = HEIGHT * 0.95
    tower_height = HEIGHT * 0.85
    
    # 分形分支算法（优化版 - 限制递归和粒子数量）
    def generate_branch(start_x, start_y, angle, length, depth, branch_angle, particles_list, max_particles=500):
        if depth <= 0 or length < 5 or len(particles_list) >= max_particles:
            return
        
        # 当前分支
        end_x = start_x + math.cos(angle) * length
        end_y = start_y + math.sin(angle) * length
        
        # 绘制分支线条（稀疏一些以防爆炸）
        steps = max(2, int(length / 5))
        for i in range(steps):
            if len(particles_list) >= max_particles:
                break
            t = i / max(1, steps - 1)
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # 颜色：绿色系，越高越亮
            green_val = int(80 + depth * 30 + t * 60)
            color = (20, min(255, green_val), min(255, green_val // 2 + 40))
            
            particles_list.append({
                'x': x, 'y': y, 'size': 2 + depth * 0.3,
                'color': color,
                'alpha': 150 + depth * 20
            })
        
        # 递归生成子分支（只生成2个而不是3个）
        if depth > 1 and len(particles_list) < max_particles * 0.8:
            new_length = length * 0.75  # 衰减系数调整为0.75（更缓和）
            # 左分支（向外扩展）
            left_angle = angle - branch_angle * 0.8
            generate_branch(end_x, end_y, left_angle, new_length, depth - 1, branch_angle, particles_list, max_particles)
            # 右分支（向外扩展）
            right_angle = angle + branch_angle * 0.8
            generate_branch(end_x, end_y, right_angle, new_length, depth - 1, branch_angle, particles_list, max_particles)
    
    # 从底部中心生成主树干，然后分支
    growth_progress = min(1.0, scene_time / 4.0)  # 4秒内完全生长
    
    # 主树干（从底部中心向上）
    trunk_height = tower_height * growth_progress * 0.35  # 树干长度缩短为35%
    trunk_steps = int(trunk_height / 5)
    for i in range(trunk_steps):
        y = tower_base_y - i * 5
        x = tower_x + math.sin(scene_time * 0.3 + i * 0.05) * 3  # 轻微摆动
        color_intensity = int(60 + i / max(1, trunk_steps) * 100)
        new_particles.append({
            'x': x, 'y': y, 'size': 3.5 - i / max(1, trunk_steps) * 1.5,
            'color': (20, min(255, color_intensity), min(255, color_intensity // 2 + 30)),
            'alpha': 200
        })
    
    # 从主树干顶部开始分支
    trunk_top_y = tower_base_y - trunk_height
    
    # 生成较少的主分支（3个而不是6个，防止爆炸）
    num_main_branches = 6
    for i in range(num_main_branches):
        if len(new_particles) > 1500:  # 限制总粒子数
            break
        branch_angle_offset = (i / num_main_branches) * math.pi * 2
        # 让分支更均匀分散（像树冠一样）
        base_angle = -math.pi / 2 + math.cos(branch_angle_offset) * 0.6
        
        branch_length = trunk_height * (0.4 + random.random() * 0.2) * growth_progress
        
        generate_branch(
            tower_x,
            trunk_top_y,
            base_angle,
            branch_length,
            3,  # 减少分形深度到3
            math.pi / 7,  # 分支角度
            new_particles,
            max_particles=600
        )
    
    return new_particles


def generate_organic_particles(particles, scene_time):
    """生成有机形态的粒子（从工业向有机转变）"""
    new_particles = []
    
    # 过渡效果：从蓝色向绿色转变
    transition = min(1.0, scene_time / 4.0)  # 4秒过渡
    
    # 生成流动的有机粒子
    for i in range(150):
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


# --- 5. 第三幕：脉动（建筑光斑，不同大小的发光泡泡）---
def generate_building_lights(particles, scene_time):
    """生成建筑光斑效果：多个不同大小的发光泡泡，呈现微妙的脉动"""
    new_particles = []
    
    # 建筑窗口网格（固定位置）
    grid_cols = 8
    grid_rows = 5
    window_spacing_x = WIDTH / (grid_cols + 1)
    window_spacing_y = HEIGHT / (grid_rows + 1)
    
    # 生成网格状窗户光斑
    for row in range(grid_rows):
        for col in range(grid_cols):
            x = (col + 1) * window_spacing_x
            y = (row + 1) * window_spacing_y
            
            # 每个窗户有随机的脉动周期
            window_id = row * grid_cols + col
            pulse_offset = window_id * 0.3
            pulse = 0.5 + 0.5 * math.sin(scene_time * 2 + pulse_offset)
            
            # 大小随机（不同的窗户大小）
            base_size = 8 + (window_id % 5) * 3
            size = base_size * (0.7 + 0.3 * pulse)
            
            # 颜色：暖金色和冷青色交替
            if window_id % 2 == 0:
                color = COLOR_WARM_GOLD
                alpha = int(80 + pulse * 120)
            else:
                color = COLOR_COOL_CYAN
                alpha = int(100 + pulse * 80)
            
            new_particles.append({
                'x': x, 'y': y, 'size': size,
                'color': color,
                'alpha': alpha
            })
    
    # 额外的散散光斑（楼外的微妙光源）
    for i in range(20):
        x = random.random() * WIDTH
        y = random.random() * HEIGHT
        
        # 这些光斑更大、更柔和
        size = 15 + random.random() * 20
        pulse = 0.5 + 0.5 * math.sin(scene_time * 1.2 + i * 0.4)
        
        # 混合颜色
        color_mix = random.choice([COLOR_WARM_GOLD, COLOR_COOL_CYAN])
        
        new_particles.append({
            'x': x, 'y': y, 'size': size * pulse,
            'color': color_mix,
            'alpha': int(40 + pulse * 60)
        })
    
    return new_particles


# --- 6. 主循环 ---
def main():
    scene_manager = SceneManager()
    running = True
    start_time = time.time()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 空格键切换场景（用于测试）
                    scene_manager.current_scene = (scene_manager.current_scene + 1) % 2
                    scene_manager.scene_start_time = current_time
        
        current_time = time.time() - start_time
        scene_num, scene_time = scene_manager.update(current_time)
        
        # 根据当前场景设置背景
        if scene_num == 0:
            FADE_SURFACE.fill(COLOR_BG_NIGHT)
            scene_name = "第一幕：共生"
        else:
            FADE_SURFACE.fill(COLOR_BG_DARK_WARM)
            scene_name = "第二幕：脉动 (建筑光斑)"
        
        FADE_SURFACE.set_alpha(FADE_ALPHA)
        SCREEN.blit(FADE_SURFACE, (0, 0))
        
        # 渲染当前场景
        all_particles = []
        
        if scene_num == 0:  # 第一幕：共生
            all_particles.extend(generate_fractal_branches([], scene_time))
            all_particles.extend(generate_organic_particles([], scene_time))
        else:  # 第二幕：脉动
            all_particles.extend(generate_building_lights([], scene_time))
        
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
        pygame.display.set_caption(f"{scene_name} | 场景 {scene_num + 1}/2 | 时间: {int(scene_time)}s | 按ESC退出")
        
        pygame.display.flip()
        CLOCK.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
