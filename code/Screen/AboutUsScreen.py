from Screen.BaseScreen import Screen
from UI.Text import Text, Font
from UI.Button import Button
from Graphic.Graphic import gfx, pygame
from Audio.AudioManager import AudioManager
from constants import *

# ===============================
# About Us Screen
# ===============================
class AboutUsScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.animation_start_time = 0
        self.animation_duration = 1000  # milliseconds
        self.current_member_index = 0
        self.member_display_time = 3000  # Hiển thị mỗi thành viên 3 giây
        self.member_start_time = 0
        self.fade_alpha = 0
        self.max_alpha = 255
        
        # Danh sách thành viên
        self.team_members = [
            {
                "name": "TRAN HAI DUC",
                "role": "Leader, Project Manager",
                "description": "Design entire game system and manage team",
                "avatar": "avatar1"  # Tên file avatar
            },
            {
                "name": "HUYNH MINH DOAN", 
                "role": "Graphics Artist",
                "description": "Design game graphics and animations",
                "avatar": "avatar2"
            },
            {
                "name": "TRAN THAI BAO",
                "role": "Sound Designer",
                "description": "Design game sound effects and music",
                "avatar": "avatar3"
            },
            {
                "name": "TRAN SO VINH",
                "role": "QA Tester & Quality Assurance",
                "description": "Test and ensure game quality",
                "avatar": "avatar4"
            }
        ]
        
        # Tạo Text objects cho tiêu đề
        self.title = Text("ABOUT US", WHITE, (SCREEN_W//2, 100), font=Font(48))
        self.subtitle = Text("Meet Our Team", GRAY, (SCREEN_W//2, 150), font=Font(24))
        
        # Tạo button Back
        self.back_button = Button(
            "BACK", 
            (30, SCREEN_H - 80), 
            120, 50,
            BLUE
        )
        
        # Tạo button Skip
        self.skip_button = Button(
            "SKIP", 
            (SCREEN_W - 150, SCREEN_H - 80), 
            120, 50,
            BLUE
        )
        
        # Text objects cho thông tin thành viên hiện tại
        self.member_name = Text("", WHITE, (SCREEN_W//2, 300), font=Font(36))
        self.member_role = Text("", YELLOW, (SCREEN_W//2, 350), font=Font(24))
        self.member_desc = Text("", GRAY, (SCREEN_W//2, 400), font=Font(18))
        
        # Surface cho fade effect
        self.fade_surface = pygame.Surface((SCREEN_W, SCREEN_H))

    def draw_background_(self, surface):
        """Vẽ background cho about us screen"""
        self.draw_background(surface)
        
        # Vẽ các hình trang trí
        self.draw_decorative_elements(surface)

    def draw_decorative_elements(self, surface):
        """Vẽ các element trang trí"""
        # Vẽ các đường viền trang trí
        pygame.draw.rect(surface, BLUE, (50, 50, SCREEN_W-100, SCREEN_H-100), 2)
        pygame.draw.rect(surface, BLUE, (60, 60, SCREEN_W-120, SCREEN_H-120), 1)
        
        # Vẽ các chấm tròn trang trí
        for i in range(5):
            x = 100 + i * 150
            y = 200
            pygame.draw.circle(surface, BLUE, (x, y), 3)

    def update_member_info(self):
        """Cập nhật thông tin thành viên hiện tại"""
        if self.current_member_index < len(self.team_members):
            member = self.team_members[self.current_member_index]
            
            # Tạo lại Text objects với nội dung mới
            self.member_name = Text(member["name"], WHITE, (SCREEN_W//2, 300), font=Font(36))
            self.member_role = Text(member["role"], YELLOW, (SCREEN_W//2, 350), font=Font(24))
            self.member_desc = Text(member["description"], GRAY, (SCREEN_W//2, 400), font=Font(18))

    def update_fade_effect(self):
        """Cập nhật hiệu ứng fade"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.member_start_time
        
        if elapsed < 500:  # Fade in
            self.fade_alpha = int((elapsed / 500) * self.max_alpha)
        elif elapsed > self.member_display_time - 500:  # Fade out
            fade_out_progress = (elapsed - (self.member_display_time - 500)) / 500
            self.fade_alpha = int(self.max_alpha * (1 - fade_out_progress))
        else:
            self.fade_alpha = self.max_alpha

    def draw_member_info(self, surface):
        """Vẽ thông tin thành viên với fade effect"""
        if self.current_member_index < len(self.team_members):
            member = self.team_members[self.current_member_index]
            
            # Tạo surface tạm cho fade effect
            temp_surface = pygame.Surface((SCREEN_W, SCREEN_H))
            temp_surface.set_alpha(self.fade_alpha)
            temp_surface.fill((0, 0, 0))
            
            # Vẽ thông tin thành viên lên surface tạm
            self.member_name.draw(temp_surface)
            self.member_role.draw(temp_surface)
            self.member_desc.draw(temp_surface)
            
            # Blit surface tạm lên surface chính
            surface.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

    def draw(self, surface):
        """Vẽ toàn bộ about us screen"""
        # Vẽ background
        self.draw_background_(surface)
        
        # Vẽ tiêu đề
        self.title.draw(surface)
        self.subtitle.draw(surface)
        
        # Vẽ thông tin thành viên
        self.draw_member_info(surface)
        
        # Vẽ progress indicator
        self.draw_progress_indicator(surface)
        
        # Vẽ buttons
        self.back_button.draw(surface)
        self.skip_button.draw(surface)

    def draw_progress_indicator(self, surface):
        """Vẽ thanh tiến trình hiển thị thành viên"""
        indicator_y = SCREEN_H - 150
        indicator_width = 200
        indicator_height = 8
        indicator_x = SCREEN_W//2 - indicator_width//2
        
        # Vẽ background của progress bar
        pygame.draw.rect(surface, GRAY, (indicator_x, indicator_y, indicator_width, indicator_height))
        
        # Vẽ progress
        if len(self.team_members) > 0:
            segment_width = indicator_width // len(self.team_members)
            for i in range(len(self.team_members)):
                x = indicator_x + i * segment_width
                color = BLUE if i <= self.current_member_index else GRAY
                pygame.draw.rect(surface, color, (x, indicator_y, segment_width-2, indicator_height))

    def update(self):
        """Cập nhật logic của about us screen"""
        current_time = pygame.time.get_ticks()
        
        # Kiểm tra xem có cần chuyển sang thành viên tiếp theo không
        if current_time - self.member_start_time >= self.member_display_time:
            self.next_member()
        
        # Cập nhật fade effect
        self.update_fade_effect()
        
        return True

    def next_member(self):
        """Chuyển sang thành viên tiếp theo"""
        self.current_member_index += 1
        if self.current_member_index >= len(self.team_members):
            # Đã hiển thị hết thành viên, quay về menu
            self.go_back()
        else:
            self.member_start_time = pygame.time.get_ticks()
            self.update_member_info()

    def go_back(self):
        """Quay về menu chính"""
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('button_click')
        self.screen_manager.set_screen("menu")

    def skip_intro(self):
        """Bỏ qua phần giới thiệu"""
        audio_manager = AudioManager.get_instance()
        audio_manager.play_sound_effect('button_click')
        self.go_back()

    def on_enter(self):
        """Được gọi khi vào about us screen"""
        # Phát nhạc nền
        audio_manager = AudioManager.get_instance()
        audio_manager.play_background_music('menu')  # Hoặc 'about_us' nếu có
        
        # Reset về thành viên đầu tiên
        self.current_member_index = 0
        self.member_start_time = pygame.time.get_ticks()
        self.animation_start_time = pygame.time.get_ticks()
        self.fade_alpha = 0
        
        # Cập nhật thông tin thành viên đầu tiên
        self.update_member_info()

    def handle_event(self, event):
        """Xử lý sự kiện input"""
        # Xử lý click buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.hit(event.pos):
                self.go_back()
            elif self.skip_button.hit(event.pos):
                self.skip_intro()
            else:
                # Click để chuyển sang thành viên tiếp theo
                self.next_member()
        
        # Xử lý phím
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_member()
            elif event.key == pygame.K_s:
                self.skip_intro()

    def on_exit(self):
        """Được gọi khi rời khỏi about us screen"""
        pass