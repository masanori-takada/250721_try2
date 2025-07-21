# Rinna-3.6B 対話システム Web版

[元のGitHubリポジトリ](https://github.com/masanori-takada/250721_try2)のRinna-3.6B LoRAファインチューニングプロジェクトをベースにした**本格的なWeb対話アプリケーション**です。

## 概要

このアプリケーションは、学習済みRinna-3.6B LoRAモデルを使用した**実用的な対話システム**です。GPU環境では実際のモデルで推論を実行し、非GPU環境ではモックAPIで動作を再現します。

## 特徴

- 🤖 **実モデル対応**: 学習済みLoRAモデルで実際の推論実行
- 🔄 **自動切替**: GPU環境では実モデル、非GPU環境ではデモ版
- 💬 **リアルタイム対話**: FastAPI + WebSocketでスムーズな対話
- 📱 **レスポンシブ**: モバイル・デスクトップ完全対応
- ⚡ **高性能**: Docker + GPU最適化
- 🎨 **プロ仕様UI**: 実用レベルのインターフェース

## 技術スタック

### フロントエンド
- **React 18** + TypeScript
- **Tailwind CSS** + Lucide Icons
- **Vite** (高速ビルド)

### バックエンド
- **FastAPI** (高性能Python API)
- **PyTorch** + Transformers + PEFT
- **Docker** + NVIDIA Docker (GPU対応)

### AI モデル
- **ベース**: rinna/japanese-gpt-neox-3.6b (3.6B parameters)
- **LoRA**: 学習済みアダプタ (12.9MB)
- **データ**: databricks-dolly-15k-ja

## クイックスタート

### 1. 自動デプロイ（推奨）

```bash
# リポジトリクローン
git clone <this-repo>
cd rinna-chat-app

# 自動セットアップ実行
chmod +x deploy/setup.sh
./deploy/setup.sh
```

### 2. 手動セットアップ

#### 学習済みモデルの配置
```bash
# 元リポジトリから学習済みモデルをダウンロード
mkdir -p backend/lora-rinna-3.6b-optimized
# adapter_model.safetensors と adapter_config.json を配置
```

#### バックエンド起動（GPU環境）
```bash
cd backend
docker-compose up -d --build
```

#### フロントエンド起動
```bash
npm install
npm run dev  # 開発モード
# または
npm run build && npm run preview  # 本番モード
```

## システム要件

### 実モデル推論（推奨）
- **GPU**: NVIDIA GPU (VRAM 14GB以上)
- **CUDA**: 11.8+
- **Docker**: NVIDIA Docker対応
- **メモリ**: 32GB+ RAM

### デモ版（最小要件）
- **CPU**: 任意
- **メモリ**: 4GB+ RAM
- **ブラウザ**: モダンブラウザ

## API仕様

### エンドポイント
- `GET /`: ヘルスチェック
- `GET /model-info`: モデル情報取得
- `POST /chat`: 対話実行
- `GET /docs`: API文書（Swagger UI）

### 対話API例
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "自然言語処理について教えて",
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

## モデル情報

- **ベースモデル**: rinna/japanese-gpt-neox-3.6b
- **ファインチューニング**: LoRA (r=8, alpha=32)
- **データセット**: databricks-dolly-15k-ja (15,015件)
- **学習時間**: 9分44秒 (A100最適化版)
- **モデルサイズ**: 12.9MB (LoRAアダプタ)

## デプロイオプション

### 1. ローカル開発
```bash
npm run dev          # フロントエンド
cd backend && python app.py  # バックエンド
```

### 2. Docker Compose（推奨）
```bash
docker-compose up -d --build
```

### 3. クラウドデプロイ
- **フロントエンド**: Netlify, Vercel, GitHub Pages
- **バックエンド**: AWS EC2 (GPU), Google Cloud (GPU), Azure (GPU)

## トラブルシューティング

### よくある問題
1. **GPU認識されない**: NVIDIA Dockerの設定確認
2. **VRAM不足**: バッチサイズやモデル量子化の調整
3. **モデル読み込みエラー**: LoRAファイルの配置確認

### ログ確認
```bash
# バックエンドログ
docker-compose logs rinna-api

# GPU使用状況
nvidia-smi
```

## 参考文献

- [元記事: Google Colab で Rinna-3.6B のLoRAファインチューニングを試す](https://note.com/npaka/n/nc387b639e50e)
- [Rinna-3.6B モデル](https://huggingface.co/rinna/japanese-gpt-neox-3.6b)
- [元GitHubリポジトリ](https://github.com/masanori-takada/250721_try2)

## ライセンス

このプロジェクトは元リポジトリの実装に基づいており、学習・研究目的で使用してください。商用利用時は各モデルのライセンスを確認してください。