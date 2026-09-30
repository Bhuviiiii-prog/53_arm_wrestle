import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35
        
        # AI surge mechanism
        self.ai_energy = 0.0
        self.ai_mode = "BUILDUP"  # BUILDUP, SURGE, EXHAUSTED
        self.ai_mode_timer = 0
        self.ai_cooldown_timer = 0
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.stamina <= 10:
                return
            
            # FIXED: Subtract to pull arm toward negative values (player's winning threshold)
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT: 
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT: 
                    self.arm_position -= 4.2
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        # Update AI pressure with dynamic surge/exhaustion cycle
        self._update_ai_pressure()

        if self.ai_mode == "SURGE":
            ai_variance = random.uniform(1.15, 1.7)
            ai_force = self.ai_strength * 2.2 * ai_variance
        elif self.ai_mode == "EXHAUSTED":
            ai_variance = random.uniform(0.18, 0.55)
            ai_force = self.ai_strength * 0.45 * ai_variance
        else:
            ai_variance = random.uniform(0.3, 1.0)
            ai_force = self.ai_strength * ai_variance

        self.arm_position += ai_force

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + 0.8)

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def _update_ai_pressure(self):
        """Manage AI energy buildup, surge cycles, and exhaustion states."""
        if self.ai_cooldown_timer > 0:
            self.ai_cooldown_timer -= 1

        if self.ai_mode == "BUILDUP":
            self.ai_energy = min(100.0, self.ai_energy + 0.75)
            if self.ai_energy >= 100.0 and self.ai_cooldown_timer <= 0:
                self.ai_mode = "SURGE"
                self.ai_mode_timer = random.randint(60, 120)
                self.ai_energy = 0.0
        elif self.ai_mode == "SURGE":
            self.ai_mode_timer -= 1
            if self.ai_mode_timer <= 0:
                self.ai_mode = "EXHAUSTED"
                self.ai_mode_timer = random.randint(75, 150)
                self.ai_cooldown_timer = random.randint(45, 90)
        else:  # EXHAUSTED
            self.ai_mode_timer -= 1
            self.ai_energy = min(100.0, self.ai_energy + 0.45)
            if self.ai_mode_timer <= 0:
                self.ai_mode = "BUILDUP"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_energy = 0.0
        self.ai_mode = "BUILDUP"
        self.ai_mode_timer = 0
        self.ai_cooldown_timer = 0

    def render(self, screen):
        screen.fill((25, 28, 35))

        # Calculate exhaustion state for visual feedback
        exhausted = self.stamina <= 10
        pulse = (pygame.time.get_ticks() // 180) % 2 == 0

        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        pygame.draw.rect(screen, (70, 30, 8), table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        # Add tremor effect when exhausted
        if exhausted:
            offset_x += math.sin(pygame.time.get_ticks() / 60.0) * 3.5
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(screen, (200, 145, 110), p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, (215, 160, 125), p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, (170, 110, 85), c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, (185, 125, 95), c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)
        # Flash red when exhausted
        if exhausted and pulse:
            bar_color = (255, 75, 75)
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)

        # Display stamina text
        stamina_text = self.font_med.render(f"{int(self.stamina)} / {int(self.max_stamina)}", True, (235, 235, 235))
        screen.blit(stamina_text, (390, 443))

        # Display exhaustion warning
        if exhausted:
            exhausted_text = self.font_med.render("EXHAUSTED!", True, (255, 90, 90) if pulse else (255, 220, 220))
            screen.blit(exhausted_text, (self.width // 2 - exhausted_text.get_width() // 2, 480))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )