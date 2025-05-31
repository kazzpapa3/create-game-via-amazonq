"""
AWS サービスアイコン認識ゲーム
ユーティリティ関数
"""
import os
import pygame
import random
import urllib.request
import zipfile
import io
import shutil

def load_aws_icons():
    """
    AWSサービスアイコンを読み込む関数
    
    実際の実装では、assets/icons ディレクトリからアイコンを読み込む
    アイコンがない場合はダミーデータを返す
    """
    icons = {}
    icons_dir = os.path.join("assets", "icons")
    
    # アイコンディレクトリが存在し、中にPNGファイルがあるか確認
    has_icons = False
    if os.path.exists(icons_dir):
        # 特に "_64@5x.png" で終わるファイルを探す
        for filename in os.listdir(icons_dir):
            if filename.endswith("_64@5x.png") and not filename.startswith("._"):
                has_icons = True
                break
    
    # 実際のアイコンがある場合は読み込む
    if has_icons:
        print("AWSサービスアイコンを読み込んでいます...")
        for filename in os.listdir(icons_dir):
            # 隠しファイルでなく、"_64@5x.png"で終わるファイルのみを対象とする
            if filename.endswith("_64@5x.png") and not filename.startswith("._"):
                # ファイル名からサービス名を抽出
                base_name = os.path.splitext(filename)[0]  # 拡張子を除去
                base_name = base_name.replace("_64@5x", "")  # サイズ指定を除去
                
                # サービス名から余分な接頭辞を削除
                if base_name.startswith("Arch_"):
                    base_name = base_name[5:]  # "Arch_" を削除
                
                # ハイフンをスペースに置換
                service_name = base_name.replace("-", " ")
                
                icon_path = os.path.join(icons_dir, filename)
                try:
                    icon = pygame.image.load(icon_path)
                    # アイコンのサイズを統一（200x200）
                    icon = pygame.transform.scale(icon, (200, 200))
                    icons[service_name] = icon
                except pygame.error:
                    print(f"警告: {icon_path} の読み込みに失敗しました")
        
        print(f"{len(icons)}個のAWSサービスアイコンを読み込みました")
    
    # アイコンがない場合はダミーデータを生成
    if not icons:
        print("AWSサービスアイコンが見つかりません。ダミーアイコンを生成します...")
        aws_services = [
            "Amazon EC2", "Amazon S3", "Amazon RDS", "Amazon DynamoDB",
            "AWS Lambda", "Amazon SQS", "Amazon SNS", "Amazon CloudWatch",
            "AWS IAM", "Amazon VPC", "Amazon Route 53", "AWS CloudFormation",
            "Amazon ECS", "Amazon EKS", "AWS Fargate", "Amazon API Gateway",
            "AWS Step Functions", "Amazon SageMaker", "AWS Glue", "Amazon Redshift"
        ]
        
        # 各サービスに対して、ダミーのアイコン（色付きの四角形）を生成
        for service in aws_services:
            # ランダムな色を生成
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            
            # 200x200のサーフェスを作成
            icon = pygame.Surface((200, 200))
            icon.fill(color)
            
            # サービス名の頭文字を描画
            font = pygame.font.SysFont('Arial', 100)
            text = font.render(service[0], True, (0, 0, 0))
            text_rect = text.get_rect(center=(100, 100))
            icon.blit(text, text_rect)
            
            icons[service] = icon
    
    return icons

def pixelate_image(image, resolution):
    """
    画像をピクセル化する関数
    
    Args:
        image: 元の画像（pygame.Surface）
        resolution: ピクセル化の解像度（256, 400, 576, 784, 1024, 1536, 2048）
    
    Returns:
        ピクセル化された画像（pygame.Surface）
    """
    # 元画像のサイズを取得
    width, height = image.get_size()
    
    # 解像度の平方根を計算（例: 256 -> 16x16）
    pixel_size = int(resolution ** 0.5)
    
    # 小さいサイズにスケールダウン
    small = pygame.transform.scale(image, (pixel_size, pixel_size))
    
    # 元のサイズにスケールアップ（ピクセル化効果）
    pixelated = pygame.transform.scale(small, (width, height))
    
    return pixelated

def download_aws_icons(url="https://d1.awsstatic.com/webteam/architecture-icons/q1-2025/Asset-Package_02072025.dee42cd0a6eaacc3da1ad9519579357fb546f803.zip"):
    """
    AWS Architecture Iconsをダウンロードして展開する関数
    
    Args:
        url: AWSアイコンのZIPファイルのURL
    """
    icons_dir = os.path.join("assets", "icons")
    
    try:
        print(f"AWSサービスアイコンをダウンロード中: {url}")
        
        # URLからZIPファイルをダウンロード
        response = urllib.request.urlopen(url)
        zip_data = io.BytesIO(response.read())
        
        # ZIPファイルを展開
        with zipfile.ZipFile(zip_data) as zip_ref:
            # 一時ディレクトリに展開
            temp_dir = os.path.join("assets", "temp")
            os.makedirs(temp_dir, exist_ok=True)
            zip_ref.extractall(temp_dir)
            
            # アイコンを探して移動
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".png") or file.endswith(".svg"):
                        # Architecture-Service-Iconsディレクトリ内のファイルのみコピー
                        if "Architecture-Service-Icons" in root:
                            src_path = os.path.join(root, file)
                            dst_path = os.path.join(icons_dir, file)
                            shutil.copy2(src_path, dst_path)
            
            # 一時ディレクトリを削除
            shutil.rmtree(temp_dir)
        
        print("AWSサービスアイコンのダウンロードと展開が完了しました")
        return True
    except Exception as e:
        print(f"エラー: AWSサービスアイコンのダウンロード中に問題が発生しました: {e}")
        return False

def create_assets_directory():
    """
    アセットディレクトリを作成する関数
    """
    icons_dir = os.path.join("assets", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # アイコンディレクトリが空かどうか確認
    is_empty = not os.listdir(icons_dir) or all(f == ".gitkeep" for f in os.listdir(icons_dir))
    
    if is_empty:
        print("アイコンディレクトリが空です。AWSサービスアイコンをダウンロードしますか？ (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            download_aws_icons()
        else:
            print("assets/icons ディレクトリを作成しました。")
            print("AWS サービスアイコンをこのディレクトリに手動で配置してください。")
    else:
        print("assets/icons ディレクトリは既に存在し、ファイルが含まれています。")

if __name__ == "__main__":
    # このファイルが直接実行された場合、アセットディレクトリを作成
    pygame.init()  # pygame初期化（フォント使用のため）
    create_assets_directory()
