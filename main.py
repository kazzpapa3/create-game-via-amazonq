#!/usr/bin/env python3
"""
AWS サービスアイコン認識ゲーム
メインエントリーポイント
"""
import os
import sys
import pygame

# 日本語フォント対応のため、環境変数を設定
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# UTF-8エンコーディングを強制
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
if sys.stderr.encoding != 'utf-8':
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

from game import Game

def check_font_availability():
    """日本語フォントの利用可能性を確認"""
    font_path = os.path.join("assets", "fonts", "ipag.ttf")
    
    if not os.path.exists(font_path):
        print("警告: 日本語フォントが見つかりません。setup.pyを実行してください。")
        print("日本語フォントをダウンロードしますか？ (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            try:
                from setup import download_japanese_font
                download_japanese_font()
            except Exception as e:
                print(f"エラー: 日本語フォントのダウンロードに失敗しました: {e}")

def main():
    """ゲームのメイン関数"""
    # PyGameの初期化
    pygame.init()
    
    # 日本語フォントの確認
    check_font_availability()
    
    # 画面サイズの設定
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    # ウィンドウのタイトル設定
    pygame.display.set_caption("AWS サービスアイコン認識ゲーム")
    
    # 利用可能なフォントの確認（デバッグ用）
    print("利用可能なフォント:")
    print(pygame.font.get_fonts())
    
    # ゲームインスタンスの作成
    game = Game(screen)
    
    # ゲームループ
    game.run()
    
    # PyGameの終了
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
