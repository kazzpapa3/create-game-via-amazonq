"""
AWS サービスアイコン認識ゲーム
ゲームのメインロジック
"""
import os
import random
import time
import pygame
from utils import load_aws_icons, pixelate_image

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Game:
    """ゲームのメインクラス"""
    def __init__(self, screen):
        """初期化"""
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        
        # 日本語対応フォントの設定
        # デフォルトフォントを先に設定（フォールバック用）
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # プロジェクトに同梱した日本語フォントを使用
        font_path = os.path.join("assets", "fonts", "ipag.ttf")
        
        if os.path.exists(font_path):
            try:
                # フォントファイルを直接読み込む
                self.font = pygame.font.Font(font_path, 24)
                self.title_font = pygame.font.Font(font_path, 36)
                print(f"日本語フォント '{font_path}' を使用します")
            except Exception as e:
                print(f"警告: 日本語フォントの読み込みに失敗しました: {e}")
                # すでにデフォルトフォントが設定されているので何もしない
        else:
            # フォントファイルが見つからない場合はシステムフォントを試す
            print(f"警告: 日本語フォントファイル '{font_path}' が見つかりません。システムフォントを試します。")
            
            # システムにインストールされているフォントを使用
            available_fonts = pygame.font.get_fonts()
            
            # 日本語フォントの候補リスト
            japanese_fonts = ['hiragino sans', 'hiragino kaku gothic pro', 'ms gothic', 
                             'meiryo', 'yu gothic', 'noto sans cjk jp', 'noto sans jp',
                             'hiraginosansgb']  # macOSで利用可能なフォントを追加
            
            # 利用可能な日本語フォントを探す
            font_name = None
            for jp_font in japanese_fonts:
                if jp_font in available_fonts:
                    font_name = jp_font
                    break
            
            if font_name:
                try:
                    self.font = pygame.font.SysFont(font_name, 24)
                    self.title_font = pygame.font.SysFont(font_name, 36)
                    print(f"システム日本語フォント '{font_name}' を使用します")
                except Exception as e:
                    print(f"警告: システム日本語フォントの読み込みに失敗しました: {e}")
                    # すでにデフォルトフォントが設定されているので何もしない
        
        self.running = True
        self.state = "menu"  # menu, playing, game_over
        
        # ゲーム設定
        self.countdown_time = 30  # 制限時間（秒）
        self.current_time = self.countdown_time
        self.score = 0
        self.combo = 0
        self.question_count = 0
        self.max_questions = 10  # 最大問題数
        
        # AWS アイコンの読み込み
        self.aws_icons = load_aws_icons()
        self.current_icon = None
        self.current_options = []
        self.correct_answer = ""
        self.selected_answer = None
        self.last_update_time = 0
        self.resolution_level = 256  # 初期解像度を256x256に変更
        self.resolution_steps = [256, 400, 576, 784, 1024, 1536, 2048]  # 解像度ステップを拡張
        self.show_original = False  # 最終的に元のアイコンを表示するフラグ
        
        # 結果表示用
        self.result_display_time = 1.0  # 結果表示時間（秒）
        self.result_time = 0
        self.result_correct = False
        
    def run(self):
        """ゲームのメインループ"""
        while self.running:
            if self.state == "menu":
                self.menu_screen()
            elif self.state == "playing":
                self.game_screen()
            elif self.state == "game_over":
                self.game_over_screen()
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def menu_screen(self):
        """メニュー画面の表示"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        self.screen.fill(WHITE)
        
        # タイトル
        title = self.title_font.render("AWS サービスアイコン認識ゲーム", True, BLACK)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title, title_rect)
        
        # 説明
        instructions = [
            "AWSサービスのアイコンを見て、正しいサービス名を選んでください。",
            "アイコンは徐々に鮮明になっていきます。",
            "早く正解するほど高得点になります！",
            "",
            "Enterキーを押してスタート",
            "ESCキーで終了"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 + i * 30))
            self.screen.blit(text, text_rect)
    
    def start_game(self):
        """ゲームの開始"""
        self.state = "playing"
        self.score = 0
        self.combo = 0
        self.question_count = 0
        self.next_question()
    
    def next_question(self):
        """次の問題を設定"""
        if self.question_count >= self.max_questions:
            self.state = "game_over"
            return
        
        self.question_count += 1
        self.current_time = self.countdown_time
        self.resolution_level = 256  # 初期解像度を256x256に設定
        self.last_update_time = time.time()
        self.show_original = False  # 元のアイコン表示フラグをリセット
        
        # ランダムにアイコンを選択
        icon_names = list(self.aws_icons.keys())
        self.correct_answer = random.choice(icon_names)
        self.current_icon = self.aws_icons[self.correct_answer]
        
        # 選択肢を作成（正解を含む4つ）
        self.current_options = [self.correct_answer]
        while len(self.current_options) < 4:
            option = random.choice(icon_names)
            if option not in self.current_options:
                self.current_options.append(option)
        
        # 選択肢をシャッフル
        random.shuffle(self.current_options)
        
        self.selected_answer = None
        self.result_time = 0
    
    def game_screen(self):
        """ゲーム画面の表示"""
        current_time = time.time()
        
        # 経過時間の計算
        if self.selected_answer is None:
            elapsed = current_time - self.last_update_time
            self.current_time -= elapsed
            self.last_update_time = current_time
            
            # 解像度の更新
            resolution_index = min(len(self.resolution_steps) - 1, 
                                  int((1 - self.current_time / self.countdown_time) * len(self.resolution_steps)))
            self.resolution_level = self.resolution_steps[resolution_index]
            
            # 時間切れに近づいたら元のアイコンを表示
            self.show_original = (self.current_time <= 3.0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and self.selected_answer is None:
                # 選択肢のクリック判定
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(self.current_options):
                    option_rect = pygame.Rect(100, 400 + i * 40, self.width - 200, 30)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_answer = option
                        self.result_correct = (option == self.correct_answer)
                        self.result_time = current_time
                        
                        if self.result_correct:
                            # スコア計算（残り時間が多いほど高得点）
                            time_bonus = int(self.current_time * 10)
                            self.combo += 1
                            combo_bonus = self.combo * 5
                            self.score += 100 + time_bonus + combo_bonus
                        else:
                            self.combo = 0
        
        self.screen.fill(WHITE)
        
        # 問題番号と残り時間の表示
        question_text = self.font.render(f"問題 {self.question_count}/{self.max_questions}", True, BLACK)
        self.screen.blit(question_text, (20, 20))
        
        time_color = BLACK if self.current_time > 5 else RED
        time_text = self.font.render(f"残り時間: {max(0, int(self.current_time))}", True, time_color)
        self.screen.blit(time_text, (self.width - 150, 20))
        
        score_text = self.font.render(f"スコア: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 50))
        
        combo_text = self.font.render(f"コンボ: {self.combo}", True, BLUE)
        self.screen.blit(combo_text, (self.width - 150, 50))
        
        # アイコンの表示（ピクセル化または元のアイコン）
        if self.current_icon:
            if self.show_original:
                # 元のアイコンをそのまま表示
                icon_rect = self.current_icon.get_rect(center=(self.width // 2, self.height // 3))
                self.screen.blit(self.current_icon, icon_rect)
            else:
                # ピクセル化したアイコンを表示
                pixelated = pixelate_image(self.current_icon, self.resolution_level)
                icon_rect = pixelated.get_rect(center=(self.width // 2, self.height // 3))
                self.screen.blit(pixelated, icon_rect)
        
        # 選択肢の表示
        option_text = self.font.render("以下から正しいAWSサービスを選んでください:", True, BLACK)
        self.screen.blit(option_text, (100, 350))
        
        for i, option in enumerate(self.current_options):
            option_rect = pygame.Rect(100, 400 + i * 40, self.width - 200, 30)
            
            # 選択後の色分け
            if self.selected_answer:
                if option == self.correct_answer:
                    pygame.draw.rect(self.screen, GREEN, option_rect)
                elif option == self.selected_answer and option != self.correct_answer:
                    pygame.draw.rect(self.screen, RED, option_rect)
                else:
                    pygame.draw.rect(self.screen, GRAY, option_rect)
            else:
                pygame.draw.rect(self.screen, GRAY, option_rect)
            
            option_text = self.font.render(option, True, BLACK)
            self.screen.blit(option_text, (110, 405 + i * 40))
        
        # 結果表示
        if self.selected_answer:
            if current_time - self.result_time >= self.result_display_time:
                self.next_question()
            else:
                result_text = "正解！" if self.result_correct else "不正解..."
                result_color = GREEN if self.result_correct else RED
                text = self.title_font.render(result_text, True, result_color)
                text_rect = text.get_rect(center=(self.width // 2, 300))
                self.screen.blit(text, text_rect)
        
        # 時間切れ
        if self.current_time <= 0:
            # まだ選択されていない場合のみ初期化処理を行う
            if self.selected_answer is None:
                self.selected_answer = ""
                self.result_correct = False
                self.result_time = current_time
                self.combo = 0
                
                # 正解の選択肢を強調表示するために、選択済み状態にする
                for i, option in enumerate(self.current_options):
                    if option == self.correct_answer:
                        pygame.draw.rect(self.screen, GREEN, pygame.Rect(100, 400 + i * 40, self.width - 200, 30))
            
            # 時間切れの表示
            time_up_text = self.title_font.render("時間切れ！", True, RED)
            time_up_rect = time_up_text.get_rect(center=(self.width // 2, 300))
            self.screen.blit(time_up_text, time_up_rect)
            
            # 正解の表示
            correct_text = self.font.render(f"正解: {self.correct_answer}", True, BLACK)
            correct_rect = correct_text.get_rect(center=(self.width // 2, 340))
            self.screen.blit(correct_text, correct_rect)
            
            # 時間切れの場合も結果表示後に次の問題へ進む
            if current_time - self.result_time >= self.result_display_time * 2:  # 表示時間を2倍に延長
                self.next_question()
    
    def game_over_screen(self):
        """ゲーム終了画面の表示"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state = "menu"
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        self.screen.fill(WHITE)
        
        # 結果表示
        game_over_text = self.title_font.render("ゲーム終了！", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.title_font.render(f"最終スコア: {self.score}", True, BLUE)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Enterキーでメニューに戻る", True, BLACK)
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height * 2 // 3))
        self.screen.blit(restart_text, restart_rect)
