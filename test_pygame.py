import pygame
import sys

print("1. 导入 pygame 成功")

try:
    pygame.init()
    print("2. pygame.init() 成功")
    
    screen = pygame.display.set_mode((800, 600))
    print("3. 创建窗口成功")
    
    pygame.display.set_caption("测试窗口")
    print("4. 设置标题成功")
    
    clock = pygame.time.Clock()
    running = True
    count = 0
    
    print("5. 进入主循环...")
    while running and count < 300:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 100))
        pygame.display.flip()
        clock.tick(60)
        count += 1
    
    print(f"6. 运行了 {count} 帧")
    pygame.quit()
    print("7. pygame.quit() 成功")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
