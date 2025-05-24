import pygame
import sys
import random

# Pygameの初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("バイクゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# バイクのクラス
class Bike(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 簡易的な四角形でバイクを表現
        self.image = pygame.Surface((50, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 100
        self.velocity_y = 0
        self.jumping = False
        self.gravity = 0.8

    def update(self):
        # 重力の適用
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # 地面との衝突判定
        if self.rect.y >= HEIGHT - 100:
            self.rect.y = HEIGHT - 100
            self.velocity_y = 0
            self.jumping = False

    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True

# 障害物のクラス
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.height = random.randint(30, 60)
        self.width = random.randint(20, 40)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = HEIGHT - 100 - self.height
        self.speed = 5

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# ゲームクラス
class Game:
    def __init__(self):
        self.bike = Bike()
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.all_sprites.add(self.bike)
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.obstacle_timer = 0
        self.game_over = False
        self.ground_y = HEIGHT - 70

    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.bike.jump()
                    if event.key == pygame.K_r and self.game_over:
                        self.__init__()  # ゲームリセット

            if not self.game_over:
                # 障害物の生成
                self.obstacle_timer += 1
                if self.obstacle_timer >= random.randint(60, 120):
                    obstacle = Obstacle()
                    self.obstacles.add(obstacle)
                    self.all_sprites.add(obstacle)
                    self.obstacle_timer = 0

                # スプライトの更新
                self.all_sprites.update()

                # 衝突判定
                if pygame.sprite.spritecollide(self.bike, self.obstacles, False):
                    self.game_over = True

                # スコア更新
                self.score += 0.1

            # 描画
            screen.fill(WHITE)
            
            # 地面の描画
            pygame.draw.rect(screen, GRAY, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
            
            # スプライトの描画
            self.all_sprites.draw(screen)
            
            # スコアの表示
            score_text = self.font.render(f"Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (10, 10))

            # ゲームオーバー表示
            if self.game_over:
                game_over_text = self.font.render("GAME OVER - Press R to restart", True, BLACK)
                screen.blit(game_over_text, (WIDTH // 2 - 180, HEIGHT // 2))

            pygame.display.flip()
            clock.tick(60)

# ゲーム実行
if __name__ == "__main__":
    game = Game()
    game.run()
