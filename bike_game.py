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
        # バイクの画像を読み込み
        try:
            self.original_image = pygame.image.load("bike.png")
            # 適切なサイズにスケール
            self.original_image = pygame.transform.scale(self.original_image, (60, 40))
            self.image = self.original_image
        except pygame.error:
            # 画像が読み込めない場合は四角形で代用
            self.image = pygame.Surface((60, 40))
            self.image.fill(BLUE)
        
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 70 - 40  # 地面位置に合わせて調整
        self.velocity_y = 0
        self.jumping = False
        self.gravity = 0.8
        self.ground_y = HEIGHT - 70 - 40  # 地面位置に合わせて調整

    def update(self):
        # 重力の適用
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # 地面との衝突判定
        if self.rect.y >= self.ground_y:
            self.rect.y = self.ground_y
            self.velocity_y = 0
            self.jumping = False

    def jump(self):
        if not self.jumping:
            self.velocity_y = -18
            self.jumping = True

# 障害物の基本クラス
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type="block"):
        super().__init__()
        self.obstacle_type = obstacle_type
        self.speed = 6
        
        if obstacle_type == "block":
            # 通常のブロック障害物
            self.width = random.randint(25, 50)
            self.height = random.randint(40, 80)
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(RED)
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH
            self.rect.y = HEIGHT - 70 - self.height
            
        elif obstacle_type == "spike":
            # トゲトゲの障害物（危険度高）
            self.width = 30
            self.height = 60
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((150, 0, 0))  # 暗い赤
            # トゲトゲのパターンを描画
            for i in range(0, self.width, 6):
                pygame.draw.polygon(self.image, (200, 0, 0), 
                                  [(i, self.height), (i+3, self.height-15), (i+6, self.height)])
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH
            self.rect.y = HEIGHT - 70 - self.height
            
        elif obstacle_type == "wall":
            # 高い壁（ジャンプ必須）
            self.width = 20
            self.height = random.randint(100, 140)
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((80, 40, 0))  # 茶色
            # レンガのパターンを描画
            for y in range(0, self.height, 20):
                for x in range(0, self.width, 10):
                    if (y // 20) % 2 == 0:
                        pygame.draw.rect(self.image, (100, 60, 20), 
                                       (x, y, 9, 19), 1)
                    else:
                        pygame.draw.rect(self.image, (100, 60, 20), 
                                       (x-5, y, 9, 19), 1)
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH
            self.rect.y = HEIGHT - 70 - self.height

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
        self.difficulty = 1

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
                # 障害物の生成（難易度に応じて種類を変更）
                self.obstacle_timer += 1
                spawn_rate = max(40, 100 - int(self.score // 50))  # スコアに応じて生成頻度上昇
                
                if self.obstacle_timer >= spawn_rate:
                    # 障害物の種類をランダムに選択
                    obstacle_types = ["block", "spike", "wall"]
                    weights = [50, 30, 20]  # 各障害物の出現確率
                    
                    # 難易度が上がると危険な障害物が多く出現
                    if self.score > 100:
                        weights = [30, 40, 30]
                    if self.score > 300:
                        weights = [20, 40, 40]
                    
                    obstacle_type = random.choices(obstacle_types, weights=weights)[0]
                    obstacle = Obstacle(obstacle_type)
                    self.obstacles.add(obstacle)
                    self.all_sprites.add(obstacle)
                    self.obstacle_timer = 0

                # スプライトの更新
                self.all_sprites.update()

                # 衝突判定
                if pygame.sprite.spritecollide(self.bike, self.obstacles, False):
                    self.game_over = True

                # スコア更新
                self.score += 0.2
                self.difficulty = int(self.score // 100) + 1

            # 描画
            screen.fill(WHITE)
            
            # 地面の描画
            pygame.draw.rect(screen, GRAY, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
            
            # スプライトの描画
            self.all_sprites.draw(screen)
            
            # スコアと難易度の表示
            score_text = self.font.render(f"Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (10, 10))
            
            difficulty_text = self.font.render(f"Level: {self.difficulty}", True, BLACK)
            screen.blit(difficulty_text, (10, 50))
            
            # 操作説明
            if self.score < 50:
                instruction_text = pygame.font.SysFont(None, 24).render("SPACE to jump!", True, BLACK)
                screen.blit(instruction_text, (10, 90))

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
