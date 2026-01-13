import pygame
import random
import math
import time

# --- 1. 初始化与参数配置 ---
pygame.init()

# 屏幕与性能设置
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("第二幕：共生 - 分形绿色脉络")
CLOCK = pygame.time.Clock()

# --- 2. 颜色配置 ---
# 工业质感（蓝色系）
COLOR_INDUSTRIAL_BLUE = (0, 100, 200)  # 工业蓝
COLOR_INDUSTRIAL_CYAN = (100, 200, 255)  # 工业青
COLOR_METAL_SILVER = (180, 190, 200)  # 金属银

# 有机形态（绿色系）
COLOR_GREEN_DARK = (20, 80, 40)  # 深绿
COLOR_GREEN_MID = (50, 150, 80)  # 中绿
COLOR_GREEN_LIGHT = (80, 200, 120)  # 浅绿
COLOR_GREEN_NEON = (100, 255, 150)  # 霓虹绿

COLOR_BG_NIGHT = (10, 20, 15)  # 夜绿背景

FADE_ALPHA = 25

# 创建背景遮罩实现长曝光拖尾
FADE_SURFACE = pygame.Surface((WIDTH, HEIGHT))
FADE_SURFACE.fill(COLOR_BG_NIGHT)
FADE_SURFACE.set_alpha(FADE_ALPHA)


# --- 3. 分形算法生成绿色脉络 ---
def generate_fractal_tree(particles_list, start_x, start_y, angle, length, depth, max_depth, branch_angle, scene_time, transition_progress):
    """递归分形算法：模拟生态根系向上攀爬"""
    if depth > max_depth or length < 2:
        return
    
    # 当前分支终点
    end_x = start_x + math.cos(angle) * length
    end_y = start_y + math.sin(angle) * length
    
    # 绘制当前分支（密集的点）
    steps = max(2, int(length / 1.5))
    for i in range(steps):
        t = i / steps
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        
        # 颜色渐变：从工业蓝到有机绿（基于过渡进度）
        # 同时从底部到顶部也有渐变（从深绿到浅绿）
        height_factor = 1.0 - (start_y / HEIGHT)  # 0（底部）到1（顶部）
        
        # 工业色（蓝色系）
        industrial_r = COLOR_INDUSTRIAL_BLUE[0]
        industrial_g = COLOR_INDUSTRIAL_BLUE[1]
        industrial_b = COLOR_INDUSTRIAL_BLUE[2]
        
        # 有机色（绿色系，基于高度和深度）
        green_base = 30 + depth * 20
        green_intensity = int(green_base + (255 - green_base) * height_factor)
        organic_r = 20
        organic_g = min(255, green_intensity)
        organic_b = min(255, green_intensity // 2 + 40)
        
        # 过渡混合
        r = int(industrial_r * (1 - transition_progress) + organic_r * transition_progress)
        g = int(industrial_g * (1 - transition_progress) + organic_g * transition_progress)
        b = int(industrial_b * (1 - transition_progress) + organic_b * transition_progress)
        
        # 大小基于深度（越细分支越小）
        size = 3 + (max_depth - depth) * 0.8
        
        # 透明度基于深度和过渡
        alpha = int(120 + depth * 30 + transition_progress * 80)
        
        particles_list.append({
            'x': x, 'y': y, 'size': size,
            'color': (r, g, b),
            'alpha': alpha
        })
    
    # 递归生成子分支
    if depth < max_depth:
        new_length = length * 0.65  # 每次分支长度减少35%
        
        # 左分支
        generate_fractal_tree(
            particles_list, end_x, end_y,
            angle - branch_angle, new_length,
            depth + 1, max_depth, branch_angle,
            scene_time, transition_progress
        )
        
        # 右分支
        generate_fractal_tree(
            particles_list, end_x, end_y,
            angle + branch_angle, new_length,
            depth + 1, max_depth, branch_angle,
            scene_time, transition_progress
        )
        
        # 继续向上（主分支）
        if depth < max_depth - 1:
            generate_fractal_tree(
                particles_list, end_x, end_y,
                angle, new_length * 0.9,
                depth + 1, max_depth, branch_angle * 0.85,
                scene_time, transition_progress
            )


def generate_organic_network(scene_time):
    """生成有机脉络网络（从底部向上攀爬）"""
    particles = []
    
    # 过渡进度：从工业向有机转变（0-1）
    transition_progress = min(1.0, scene_time / 12.0)  # 12秒完成过渡
    
    # 信标塔/建筑物中心位置
    tower_x = WIDTH / 2
    tower_base_y = HEIGHT * 0.95  # 底部
    tower_height = HEIGHT * 0.85  # 总高度
    
    # 生长进度：从底部向上生长
    growth_progress = min(1.0, scene_time / 10.0)  # 10秒内完全生长
    current_height = tower_height * growth_progress
    
    # 主树干（从底部中心向上）
    trunk_length = current_height * 0.3
    trunk_steps = int(trunk_length / 3)
    
    for i in range(trunk_steps):
        y = tower_base_y - i * 3
        x = tower_x + math.sin(scene_time * 0.3 + i * 0.05) * 3  # 轻微摆动
        
        height_factor = 1.0 - (y / HEIGHT)
        
        # 颜色过渡
        industrial_color = COLOR_INDUSTRIAL_BLUE
        organic_green = 30 + int(height_factor * 150)
        organic_color = (20, min(255, organic_green), min(255, organic_green // 2 + 40))
        
        r = int(industrial_color[0] * (1 - transition_progress) + organic_color[0] * transition_progress)
        g = int(industrial_color[1] * (1 - transition_progress) + organic_color[1] * transition_progress)
        b = int(industrial_color[2] * (1 - transition_progress) + organic_color[2] * transition_progress)
        
        particles.append({
            'x': x, 'y': y, 'size': 5 - i / trunk_steps * 2,
            'color': (r, g, b),
            'alpha': int(200 + transition_progress * 55)
        })
    
    # 从主树干顶部生成分形分支
    trunk_top_y = tower_base_y - trunk_length
    
    # 生成多个主分支（从树干向四周展开）
    num_main_branches = 8
    for i in range(num_main_branches):
        # 角度分布：主要向上，略微分散
        base_angle = math.pi / 2 - 0.25 + (i / num_main_branches) * 0.5
        
        # 分支长度基于生长进度
        branch_length = current_height * (0.35 + random.random() * 0.25)
        
        # 递归生成分形树
        generate_fractal_tree(
            particles,
            tower_x,
            trunk_top_y,
            base_angle,
            branch_length,
            0,  # 初始深度
            6,  # 最大深度（更多细节）
            math.pi / 5,  # 分支角度
            scene_time,
            transition_progress
        )
    
    # 添加额外的有机粒子（填充效果）
    if transition_progress > 0.3:
        for i in range(int(300 * transition_progress)):
            x = WIDTH / 2 + (random.random() - 0.5) * WIDTH * 0.6
            y = HEIGHT * 0.3 + random.random() * HEIGHT * 0.5
            
            # 流动效果
            wave_x = math.sin(scene_time * 1.5 + x * 0.01) * 15
            wave_y = math.cos(scene_time * 1.2 + y * 0.01) * 10
            x += wave_x
            y += wave_y
            
            # 纯绿色（有机形态）
            green_intensity = 80 + int(random.random() * 120)
            particles.append({
                'x': x, 'y': y, 'size': 2 + random.random() * 2,
                'color': (20, min(255, green_intensity), min(255, green_intensity // 2 + 50)),
                'alpha': int(80 * transition_progress)
            })
    
    return particles


# --- 4. 主循环 ---
def main():
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
        
        # 渲染背景（拖尾效果）
        FADE_SURFACE.fill(COLOR_BG_NIGHT)
        FADE_SURFACE.set_alpha(FADE_ALPHA)
        SCREEN.blit(FADE_SURFACE, (0, 0))
        
        # 生成有机脉络网络
        all_particles = generate_organic_network(current_time)
        
        # 绘制所有粒子
        for p in all_particles:
            if 0 <= p['x'] < WIDTH and 0 <= p['y'] < HEIGHT:
                # 创建半透明表面
                particle_surface = pygame.Surface((int(p['size'] * 4), int(p['size'] * 4)), pygame.SRCALPHA)
                color_with_alpha = (*p['color'], p.get('alpha', 255))
                pygame.draw.circle(particle_surface, color_with_alpha,
                                 (int(p['size'] * 2), int(p['size'] * 2)),
                                 int(p['size']))
                
                # 外发光效果
                glow_surface = pygame.Surface((int(p['size'] * 6), int(p['size'] * 6)), pygame.SRCALPHA)
                glow_alpha = p.get('alpha', 255) // 3
                glow_color = (*p['color'], glow_alpha)
                pygame.draw.circle(glow_surface, glow_color,
                                 (int(p['size'] * 3), int(p['size'] * 3)),
                                 int(p['size'] * 2))
                SCREEN.blit(glow_surface,
                           (int(p['x'] - p['size'] * 3), int(p['y'] - p['size'] * 3)),
                           special_flags=pygame.BLEND_ADD)
                
                SCREEN.blit(particle_surface,
                           (int(p['x'] - p['size'] * 2), int(p['y'] - p['size'] * 2)),
                           special_flags=pygame.BLEND_ADD)
        
        # 显示信息
        transition = min(1.0, current_time / 12.0)
        pygame.display.set_caption(f"第二幕：共生 | 过渡进度: {int(transition * 100)}% | 时间: {int(current_time)}s | 按ESC退出")
        
        pygame.display.flip()
        CLOCK.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
