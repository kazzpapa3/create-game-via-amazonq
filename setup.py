#!/usr/bin/env python3
"""
AWS サービスアイコン認識ゲーム
セットアップスクリプト
"""
import os
import sys
import shutil
import urllib.request
import zipfile
import io
import subprocess
import platform

def check_python_version():
    """Pythonのバージョンを確認する関数"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"エラー: Python {required_version[0]}.{required_version[1]} 以上が必要です。")
        print(f"現在のバージョン: Python {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    
    print(f"Python {current_version[0]}.{current_version[1]}.{current_version[2]} を使用しています。")
    return True

def check_pygame():
    """PyGameがインストールされているか確認する関数"""
    try:
        import pygame
        print(f"PyGame {pygame.version.ver} がインストールされています。")
        return True
    except ImportError:
        print("PyGameがインストールされていません。")
        print("仮想環境を有効化し、'pip install -r requirements.txt' を実行してください。")
        return False

def create_assets_directory():
    """アセットディレクトリを作成する関数"""
    # アセットディレクトリの作成
    assets_dir = "assets"
    icons_dir = os.path.join(assets_dir, "icons")
    fonts_dir = os.path.join(assets_dir, "fonts")
    
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(fonts_dir, exist_ok=True)
    
    print("アセットディレクトリを作成しました。")
    return True

def download_japanese_font():
    """日本語フォントをダウンロードする関数"""
    fonts_dir = os.path.join("assets", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    
    font_path = os.path.join(fonts_dir, "ipag.ttf")
    
    # フォントが既に存在するか確認
    if os.path.exists(font_path):
        print("日本語フォントは既にダウンロード済みです")
        return True
    
    # IPAゴシックフォントをダウンロード
    font_url = "https://moji.or.jp/wp-content/ipafont/IPAfont/ipag00303.zip"
    try:
        print(f"日本語フォント(IPAゴシック)をダウンロード中: {font_url}")
        
        # 一時ファイルにダウンロード
        temp_zip = os.path.join(fonts_dir, "temp_font.zip")
        urllib.request.urlretrieve(font_url, temp_zip)
        
        # ZIPファイルを展開
        with zipfile.ZipFile(temp_zip) as zip_ref:
            # 一時ディレクトリに展開
            temp_dir = os.path.join(fonts_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            zip_ref.extractall(temp_dir)
            
            # フォントファイルを移動
            extracted_font = os.path.join(temp_dir, "ipag00303", "ipag.ttf")
            if os.path.exists(extracted_font):
                shutil.copy2(extracted_font, font_path)
                print(f"フォントファイルを {font_path} にコピーしました")
            else:
                print(f"エラー: 展開したフォントファイルが見つかりません: {extracted_font}")
                return False
            
            # 一時ファイルとディレクトリを削除
            shutil.rmtree(temp_dir)
            os.remove(temp_zip)
        
        print("日本語フォントのダウンロードが完了しました")
        return True
    except Exception as e:
        print(f"エラー: 日本語フォントのダウンロード中に問題が発生しました: {e}")
        return False

def download_aws_icons():
    """
    AWS Architecture Iconsをダウンロードして展開する関数
    """
    icons_dir = os.path.join("assets", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # アイコンURLの設定
    url = "https://d1.awsstatic.com/webteam/architecture-icons/q1-2025/Asset-Package_02072025.dee42cd0a6eaacc3da1ad9519579357fb546f803.zip"
    
    try:
        print(f"AWSサービスアイコンをダウンロード中: {url}")
        
        # URLからZIPファイルをダウンロード
        temp_zip = os.path.join(icons_dir, "temp_icons.zip")
        urllib.request.urlretrieve(url, temp_zip)
        
        # ZIPファイルを展開
        with zipfile.ZipFile(temp_zip) as zip_ref:
            # 一時ディレクトリに展開
            temp_dir = os.path.join(icons_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            zip_ref.extractall(temp_dir)
            
            # アイコンを探して移動
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith("_64@5x.png") and not file.startswith("._"):
                        # Architecture-Service-Iconsディレクトリ内のファイルのみコピー
                        if "Architecture-Service-Icons" in root:
                            src_path = os.path.join(root, file)
                            dst_path = os.path.join(icons_dir, file)
                            shutil.copy2(src_path, dst_path)
            
            # 一時ディレクトリとZIPファイルを削除
            shutil.rmtree(temp_dir)
            os.remove(temp_zip)
        
        print("AWSサービスアイコンのダウンロードと展開が完了しました")
        return True
    except Exception as e:
        print(f"エラー: AWSサービスアイコンのダウンロード中に問題が発生しました: {e}")
        return False

def check_virtual_env():
    """仮想環境が有効化されているか確認する関数"""
    # 仮想環境が有効化されているか確認
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("仮想環境が有効化されています。")
        return True
    else:
        print("警告: 仮想環境が有効化されていません。")
        print("以下のコマンドで仮想環境を有効化することをお勧めします：")
        if platform.system() == "Windows":
            print("pygame-env\\Scripts\\activate")
        else:
            print("source pygame-env/bin/activate")
        return False

def install_requirements():
    """必要なパッケージをインストールする関数"""
    if not os.path.exists("requirements.txt"):
        print("requirements.txtが見つかりません。")
        return False
    
    try:
        print("必要なパッケージをインストールしています...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("パッケージのインストールが完了しました。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: パッケージのインストール中に問題が発生しました: {e}")
        return False

def main():
    """セットアップ関数"""
    # UTF-8エンコーディングを強制
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
    
    print("AWS サービスアイコン認識ゲームのセットアップを開始します...")
    
    # Pythonバージョンの確認
    if not check_python_version():
        sys.exit(1)
    
    # 仮想環境の確認
    check_virtual_env()
    
    # 必要なパッケージのインストール
    install_requirements()
    
    # PyGameの確認
    try:
        import pygame
        pygame.init()
    except ImportError:
        print("PyGameのインポートに失敗しました。")
        print("'pip install pygame' を実行してください。")
        sys.exit(1)
    
    # アセットディレクトリの作成
    create_assets_directory()
    
    # 日本語フォントのダウンロード
    download_japanese_font()
    
    # AWS公式アイコンのダウンロード
    icons_dir = os.path.join("assets", "icons")
    if os.path.exists(icons_dir):
        # アイコンディレクトリが空かどうか確認
        icon_files = [f for f in os.listdir(icons_dir) if f.endswith("_64@5x.png")]
        if not icon_files:
            print("AWS公式アイコンをダウンロードしますか？ (y/n)")
            response = input().strip().lower()
            
            if response == 'y':
                download_aws_icons()
        else:
            print(f"AWS公式アイコンは既にダウンロード済みです（{len(icon_files)}個のアイコンが見つかりました）")
    
    print("\nセットアップが完了しました。")
    print("ゲームを開始するには、以下のコマンドを実行してください：")
    print("python main.py")

if __name__ == "__main__":
    main()
