#!/usr/bin/env python3
"""
Rinna-3.6B LoRAファインチューニング環境セットアップ
参考: https://note.com/npaka/n/nc387b639e50e
"""

import subprocess
import sys
import os

def install_packages():
    """必要なパッケージのインストール"""
    print("=== 必要なパッケージのインストール ===")
    
    # PEFTのインストール（最新版）
    print("PEFTをインストール中...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-Uqq", 
        "git+https://github.com/huggingface/peft.git"
    ])
    
    # 基本パッケージのインストール
    packages = [
        "transformers", "datasets", "accelerate", "bitsandbytes", "sentencepiece"
    ]
    
    for package in packages:
        print(f"{package}をインストール中...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-Uqq", package
        ])
    
    print("パッケージのインストール完了")

def check_gpu():
    """GPU環境の確認"""
    print("\n=== GPU環境の確認 ===")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f}GB)")
        else:
            print("警告: CUDAが利用できません")
            print("このスクリプトは大量のVRAM（14GB以上）を必要とします")
            
    except ImportError:
        print("PyTorchがインストールされていません")

def create_directories():
    """必要なディレクトリの作成"""
    print("\n=== ディレクトリの作成 ===")
    
    directories = [
        "lora-rinna-3.6b",
        "lora-rinna-3.6b-results",
        "cache",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"ディレクトリ作成: {directory}")

def check_environment():
    """環境の確認"""
    print("\n=== 環境の確認 ===")
    
    try:
        import transformers
        import datasets
        import peft
        import torch
        
        print(f"transformers: {transformers.__version__}")
        print(f"datasets: {datasets.__version__}")
        print(f"peft: {peft.__version__}")
        print(f"torch: {torch.__version__}")
        
        print("✅ 必要なライブラリが正常にインストールされています")
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    
    return True

def show_requirements():
    """必要環境の表示"""
    print("\n=== 必要環境 ===")
    print("• Google Colab Pro/Pro+ A100 推奨")
    print("• VRAM: 14.0GB以上")
    print("• Python: 3.8以上")
    print("• CUDA対応GPU")
    print("\n注意: ローカル環境では相当なスペックが必要です")

def main():
    """メイン処理"""
    print("Rinna-3.6B LoRA環境セットアップ")
    print("参考: https://note.com/npaka/n/nc387b639e50e")
    print("=" * 50)
    
    # 必要環境の表示
    show_requirements()
    
    # ユーザー確認（自動実行用）
    print("\n自動実行モードで続行します...")
    response = "y"
    
    # パッケージのインストール
    install_packages()
    
    # ディレクトリの作成
    create_directories()
    
    # GPU環境の確認
    check_gpu()
    
    # 環境の確認
    if check_environment():
        print("\n✅ 環境セットアップが完了しました")
        print("\n次のステップ:")
        print("1. python rinna_3_6b_lora_training.py  # 学習実行")
        print("2. python rinna_3_6b_inference.py     # 推論実行")
    else:
        print("\n❌ 環境セットアップに問題があります")

if __name__ == "__main__":
    main() 