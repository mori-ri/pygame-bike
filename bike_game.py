import pygame
import sys
import random
import os

# Pygameの初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("バイクゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# 日本語フォントの設定
def get_japanese_font(size):
    """日本語をサポートするフォントを取得"""
    # まず、macOSのシステムフォントファイルから直接読み込みを試行
    font_paths = [
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
        '/System/Library/Fonts/Arial Unicode.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial Unicode MS.ttf'
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, size)
                # 日本語テスト
                test_surface = font.render("バイクゲーム", True, (0, 0, 0))
                if test_surface.get_width() > 0:
                    return font
        except Exception as e:
            print(f"Font file {font_path} failed: {e}")
            continue
    
    # macOS用の確実な日本語フォント候補
    font_candidates = [
        'AppleGothic',          # macOS標準日本語フォント
        'HiraginoSans-W3',      # macOS Hiragino Sans
        'Hiragino Sans',        # macOS Hiragino Sans
        'HiraginoSans-W6',      # macOS Hiragino Sans Bold
        'Arial Unicode MS',     # macOS Arial Unicode
        'Helvetica',            # macOS標準フォント
        'System Font',          # システムフォント
        None                    # pygame デフォルト
    ]
    
    for font_name in font_candidates:
        try:
            if font_name:
                font = pygame.font.SysFont(font_name, size)
            else:
                font = pygame.font.Font(None, size)
            
            # より確実な日本語文字テスト
            test_texts = ["あ", "バイク", "ゲーム"]
            all_valid = True
            
            for test_text in test_texts:
                try:
                    test_surface = font.render(test_text, True, (0, 0, 0))
                    if test_surface.get_width() <= 0 or test_surface.get_height() <= 0:
                        all_valid = False
                        break
                except:
                    all_valid = False
                    break
            
            if all_valid:
                print(f"Using font: {font_name if font_name else 'Default pygame font'}")
                return font
                
        except Exception as e:
            print(f"Font {font_name} failed: {e}")
            continue
    
    # 最終手段：強制的にデフォルトフォントを使用
    print("Warning: No suitable Japanese font found, using default")
    return pygame.font.Font(None, size)

# バイクのクラス
class Bike(pygame.sprite.Sprite):
    def __init__(self, bike_type="bike1", player_id=1):
        super().__init__()
        self.player_id = player_id
        self.crashed = False
        
        # バイク画像の読み込み
        try:
            if bike_type == "bike1":
                self.original_image = pygame.image.load("bike.png")
            else:
                self.original_image = pygame.image.load("bike2.png")
                # bike2の画像を左右反転
                self.original_image = pygame.transform.flip(self.original_image, True, False)
            # 適切なサイズにスケール
            self.original_image = pygame.transform.scale(self.original_image, (80, 50))
            self.image = self.original_image
        except pygame.error:
            # 画像が読み込めない場合は四角形で代用
            self.image = pygame.Surface((60, 40))
            self.image.fill(BLUE if player_id == 1 else GREEN)
            print(f"Warning: Could not load {bike_type} image. Using default.")
        
        self.rect = self.image.get_rect()
        # プレイヤー1は左側、プレイヤー2は右側に配置
        self.rect.x = 80 if player_id == 1 else 120
        self.rect.y = HEIGHT - 140 - 40  # 地面位置に合わせて調整
        self.velocity_y = 0
        self.jumping = False
        self.gravity = 0.8
        self.ground_y = HEIGHT - 140 - 40  # 地面位置に合わせて調整

    def update(self, slopes=None):
        if self.crashed:
            return
            
        # 重力の適用
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # 坂を考慮した地面の高さを計算
        current_ground_y = self.ground_y
        if slopes:
            for slope in slopes:
                # バイクが坂の範囲内にいるかチェック
                if (slope.rect.x <= self.rect.centerx <= slope.rect.right):
                    current_ground_y = slope.get_ground_height_at_x(self.rect.centerx) - self.rect.height
                    break

        # 地面との衝突判定
        if self.rect.y >= current_ground_y:
            self.rect.y = current_ground_y
            self.velocity_y = 0
            self.jumping = False

    def jump(self):
        if not self.jumping and not self.crashed:
            self.velocity_y = -18
            self.jumping = True
    
    def crash(self):
        self.crashed = True
        # クラッシュ時の視覚効果（赤くする）
        if hasattr(self, 'original_image'):
            self.image = self.original_image.copy()
            self.image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)

# 坂のクラス
class Slope(pygame.sprite.Sprite):
    def __init__(self, slope_type="up"):
        super().__init__()
        self.slope_type = slope_type
        self.speed = 6
        self.width = 150
        self.height = 80
        
        # 坂のサーフェースを作成
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if slope_type == "up":
            # 上り坂（左が低く、右が高い）
            points = [(0, self.height), (self.width, 0), (self.width, self.height)]
            pygame.draw.polygon(self.image, (101, 67, 33), points)  # 茶色
            pygame.draw.polygon(self.image, (139, 115, 85), points, 3)  # 境界線
        elif slope_type == "down":
            # 下り坂（左が高く、右が低い）
            points = [(0, 0), (self.width, self.height), (0, self.height)]
            pygame.draw.polygon(self.image, (101, 67, 33), points)  # 茶色
            pygame.draw.polygon(self.image, (139, 115, 85), points, 3)  # 境界線
        
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = HEIGHT - 140 - self.height
        
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
    
    def get_ground_height_at_x(self, x):
        """指定されたx座標での坂の地面の高さを取得"""
        relative_x = x - self.rect.x
        if relative_x < 0 or relative_x > self.width:
            return HEIGHT - 140  # 坂の範囲外は通常の地面の高さ
        
        if self.slope_type == "up":
            # 上り坂：x座標が増えるほど高くなる
            slope_height = (relative_x / self.width) * self.height
            return self.rect.y + self.height - slope_height
        elif self.slope_type == "down":
            # 下り坂：x座標が増えるほど低くなる
            slope_height = (relative_x / self.width) * self.height
            return self.rect.y + slope_height

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
            self.rect.y = HEIGHT - 140 - self.height
            
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
            self.rect.y = HEIGHT - 140 - self.height
            
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
            self.rect.y = HEIGHT - 140 - self.height

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# バイク選択画面クラス
class BikeSelection:
    def __init__(self):
        self.font = get_japanese_font(48)
        self.small_font = get_japanese_font(32)
        self.selected = 0  # 0: 1人プレイ, 1: 2人プレイ
        
        # バイク画像の読み込み
        try:
            self.bike1_img = pygame.image.load("bike.png")
            self.bike1_img = pygame.transform.scale(self.bike1_img, (160, 100))
        except pygame.error:
            self.bike1_img = pygame.Surface((160, 100))
            self.bike1_img.fill(BLUE)
            print("Warning: Could not load bike.png. Using default.")
            
        try:
            self.bike2_img = pygame.image.load("bike2.png")
            self.bike2_img = pygame.transform.scale(self.bike2_img, (160, 100))
            # bike2の画像を左右反転
            self.bike2_img = pygame.transform.flip(self.bike2_img, True, False)
        except pygame.error:
            self.bike2_img = pygame.Surface((160, 100))
            self.bike2_img.fill(GREEN)
            print("Warning: Could not load bike2.png. Using default.")
    
    def run(self):
        selection_done = False
        
        while not selection_done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.selected = 0
                    elif event.key == pygame.K_RIGHT:
                        self.selected = 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        selection_done = True
            
            # 描画
            screen.fill(WHITE)
            
            # タイトル
            title_text = self.font.render("プレイモードを選んでください", True, BLACK)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
            
            # 1人プレイ
            player1_pos = (WIDTH // 4 - self.bike1_img.get_width() // 2, HEIGHT // 2 - 50)
            screen.blit(self.bike1_img, player1_pos)
            player1_text = self.small_font.render("1人プレイ", True, BLACK)
            screen.blit(player1_text, (WIDTH // 4 - player1_text.get_width() // 2, HEIGHT // 2 + 70))
            
            # 2人プレイ
            player2_pos = (WIDTH * 3 // 4 - 80, HEIGHT // 2 - 50)
            # 2台のバイクを並べて描画
            bike1_small = pygame.transform.scale(self.bike1_img, (80, 50))
            bike2_small = pygame.transform.scale(self.bike2_img, (80, 50))
            screen.blit(bike1_small, player2_pos)
            screen.blit(bike2_small, (player2_pos[0] + 80, player2_pos[1]))
            
            player2_text = self.small_font.render("2人プレイ", True, BLACK)
            screen.blit(player2_text, (WIDTH * 3 // 4 - player2_text.get_width() // 2, HEIGHT // 2 + 70))
            
            # 選択枠の描画
            if self.selected == 0:
                pygame.draw.rect(screen, RED, (player1_pos[0] - 10, player1_pos[1] - 10, 
                                             self.bike1_img.get_width() + 20, 
                                             self.bike1_img.get_height() + 20), 3)
            else:
                pygame.draw.rect(screen, RED, (player2_pos[0] - 10, player2_pos[1] - 10, 
                                             160 + 20, 
                                             50 + 20), 3)
            
            # 操作説明
            instruction_text = self.small_font.render("← →キーで選択、Spaceキーで決定", True, BLACK)
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))
            
            pygame.display.flip()
        
        # 選択されたモードを返す
        return "single" if self.selected == 0 else "two_player"

# ゲームクラス
class Game:
    def __init__(self, game_mode):
        self.game_mode = game_mode
        
        if game_mode == "single":
            self.bike1 = Bike("bike1", 1)
            self.bike2 = None
            self.bikes = [self.bike1]
        else:  # two_player
            self.bike1 = Bike("bike1", 1)
            self.bike2 = Bike("bike2", 2)
            self.bikes = [self.bike1, self.bike2]
        
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.slopes = pygame.sprite.Group()
        
        for bike in self.bikes:
            self.all_sprites.add(bike)
            
        self.score = 0
        self.font = get_japanese_font(36)
        self.small_font = get_japanese_font(24)
        self.obstacle_timer = 0
        self.slope_timer = 0
        self.game_over = False
        self.ground_y = HEIGHT - 140
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
                        if self.game_mode == "single":
                            self.bike1.jump()
                    # 2人プレイの場合のキー入力
                    elif event.key == pygame.K_LMETA or event.key == pygame.K_RMETA:  # Cmdキー
                        if self.bike1:
                            self.bike1.jump()
                    elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:  # Optionキー
                        if self.bike2:
                            self.bike2.jump()
                    elif event.key == pygame.K_r and self.game_over:
                        # ゲームリセット（バイク選択画面に戻る）
                        return True

            if not self.game_over:
                # 障害物の生成（難易度を下げるため壁の出現確率を下げる）
                self.obstacle_timer += 1
                spawn_rate = max(40, 100 - int(self.score // 50))  # スコアに応じて生成頻度上昇
                
                if self.obstacle_timer >= spawn_rate:
                    # 障害物の種類をランダムに選択（壁の確率を大幅に下げる）
                    obstacle_types = ["block", "spike", "wall"]
                    weights = [60, 35, 5]  # 壁の出現確率を20%から5%に下げる
                    
                    # 難易度が上がっても壁の確率は低く保つ
                    if self.score > 100:
                        weights = [50, 40, 10]
                    if self.score > 300:
                        weights = [40, 45, 15]
                    
                    obstacle_type = random.choices(obstacle_types, weights=weights)[0]
                    obstacle = Obstacle(obstacle_type)
                    self.obstacles.add(obstacle)
                    self.all_sprites.add(obstacle)
                    self.obstacle_timer = 0

                # 坂の生成
                self.slope_timer += 1
                slope_spawn_rate = 200  # 坂の生成頻度（フレーム数）
                
                if self.slope_timer >= slope_spawn_rate and random.random() < 0.7:  # 70%の確率で坂を生成
                    slope_type = random.choice(["up", "down"])
                    slope = Slope(slope_type)
                    self.slopes.add(slope)
                    self.all_sprites.add(slope)
                    self.slope_timer = 0

                # スプライトの更新（バイクに坂の情報を渡す）
                for bike in self.bikes:
                    bike.update(self.slopes)
                    
                self.obstacles.update()
                self.slopes.update()

                # 衝突判定（各バイク個別に判定）
                for bike in self.bikes:
                    if not bike.crashed and pygame.sprite.spritecollide(bike, self.obstacles, False):
                        bike.crash()

                # 全バイクがクラッシュしたかチェック
                all_crashed = all(bike.crashed for bike in self.bikes)
                if all_crashed:
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
            
            # プレイヤー状態の表示
            if self.game_mode == "two_player":
                player1_status = "Player1: " + ("CRASHED" if self.bike1.crashed else "OK")
                player2_status = "Player2: " + ("CRASHED" if self.bike2.crashed else "OK")
                
                player1_color = RED if self.bike1.crashed else GREEN
                player2_color = RED if self.bike2.crashed else GREEN
                
                p1_text = self.small_font.render(player1_status, True, player1_color)
                p2_text = self.small_font.render(player2_status, True, player2_color)
                
                screen.blit(p1_text, (WIDTH - 200, 10))
                screen.blit(p2_text, (WIDTH - 200, 35))
            
            # 操作説明
            if self.score < 50:
                if self.game_mode == "single":
                    instruction_text = self.small_font.render("SPACE to jump!", True, BLACK)
                    screen.blit(instruction_text, (10, 90))
                else:
                    instruction_text1 = self.small_font.render("Player1: Cmd to jump!", True, BLACK)
                    instruction_text2 = self.small_font.render("Player2: Option to jump!", True, BLACK)
                    screen.blit(instruction_text1, (10, 90))
                    screen.blit(instruction_text2, (10, 115))

            # ゲームオーバー表示
            if self.game_over:
                game_over_text = self.font.render("GAME OVER - Press R to restart", True, BLACK)
                screen.blit(game_over_text, (WIDTH // 2 - 180, HEIGHT // 2))

            pygame.display.flip()
            clock.tick(60)
            
        return False

# メインループ
if __name__ == "__main__":
    restart = True
    
    while restart:
        # バイク選択画面
        bike_selection = BikeSelection()
        selected_mode = bike_selection.run()
        
        # ゲーム開始
        game = Game(selected_mode)
        restart = game.run()
