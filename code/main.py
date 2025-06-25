import pygame
import sys

# khởi tạo pygame
pygame.init()

# cấu hình màn hình
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Di chuyển ảnh PNG")

# tải ảnh PNG
image = pygame.image.load("resource/Tiny Swords (Free Pack)/Units/Black Units/Warrior/Warrior_Attack1.png").convert_alpha()
image_rect = image.get_rect()
image_rect.topleft = (100, 100)  # vị trí ban đầu

# tốc độ di chuyển
speed = 5

# vòng lặp chính
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # lấy các phím đang được nhấn
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        image_rect.x -= speed
    if keys[pygame.K_RIGHT]:
        image_rect.x += speed
    if keys[pygame.K_UP]:
        image_rect.y -= speed
    if keys[pygame.K_DOWN]:
        image_rect.y += speed

    # vẽ lại màn hình
    screen.fill((30, 30, 30))  # nền xám
    screen.blit(image, image_rect)
    pygame.display.update()

    # giới hạn fps
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
