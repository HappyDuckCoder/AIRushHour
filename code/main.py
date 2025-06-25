import pygame
import sys

# hàm scale ảnh theo kích thước cố định
def scale_image(image: pygame.Surface, width: int, height: int) -> pygame.Surface:
    return pygame.transform.scale(image, (width, height))

# khởi tạo pygame
pygame.init()

# cấu hình màn hình
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
pygame.display.set_caption("Double Buffering - Di chuyển nhân vật")

# load và scale ảnh nền
background = pygame.image.load("image2.png").convert()
background = scale_image(background, screen_width, screen_height)

# load và scale nhân vật
character = pygame.image.load("image1.png").convert_alpha()
character = scale_image(character, 64, 64)  # nhân vật 64x64

# toạ độ ban đầu của nhân vật
char_rect = character.get_rect()
char_rect.topleft = (100, 100)

# tốc độ di chuyển
speed = 5

# đồng hồ giới hạn FPS
clock = pygame.time.Clock()

# vòng lặp chính
running = True
while running:
    # xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # xử lý phím nhấn
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        char_rect.x -= speed
    if keys[pygame.K_RIGHT]:
        char_rect.x += speed
    if keys[pygame.K_UP]:
        char_rect.y -= speed
    if keys[pygame.K_DOWN]:
        char_rect.y += speed

    # giới hạn nhân vật trong màn hình
    char_rect.x = max(0, min(screen_width - char_rect.width, char_rect.x))
    char_rect.y = max(0, min(screen_height - char_rect.height, char_rect.y))

    # vẽ nền và nhân vật (double buffering)
    screen.blit(background, (0, 0))
    screen.blit(character, char_rect.topleft)
    pygame.display.flip()

    # giới hạn FPS
    clock.tick(60)

# thoát
pygame.quit()
sys.exit()
