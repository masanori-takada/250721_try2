#!/bin/bash
# Rinna-3.6B 対話システム デプロイスクリプト

set -e

echo "🚀 Rinna-3.6B 対話システム デプロイ開始"

# 1. 学習済みモデルのダウンロード
echo "📥 学習済みLoRAモデルをダウンロード中..."
if [ ! -d "backend/lora-rinna-3.6b-optimized" ]; then
    mkdir -p backend/lora-rinna-3.6b-optimized
    
    # GitHubから学習済みモデルをダウンロード
    # 注意: 実際のファイルは大きいため、Git LFSまたは別の方法でダウンロード
    echo "⚠️  学習済みモデルファイルを手動で配置してください:"
    echo "   backend/lora-rinna-3.6b-optimized/adapter_model.safetensors"
    echo "   backend/lora-rinna-3.6b-optimized/adapter_config.json"
fi

# 2. 環境設定
echo "⚙️  環境設定..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env ファイルを作成しました"
fi

# 3. Docker環境の確認
echo "🐳 Docker環境の確認..."
if ! command -v docker &> /dev/null; then
    echo "❌ Dockerがインストールされていません"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Composeがインストールされていません"
    exit 1
fi

# 4. NVIDIA Docker の確認
echo "🎮 NVIDIA Docker の確認..."
if ! docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi &> /dev/null; then
    echo "⚠️  NVIDIA Docker が正しく設定されていません"
    echo "   GPU推論には NVIDIA Docker が必要です"
fi

# 5. フロントエンドのビルド
echo "🏗️  フロントエンドをビルド中..."
npm install
npm run build

# 6. バックエンドの起動
echo "🚀 バックエンドAPIを起動中..."
cd backend
docker-compose up -d --build

echo "✅ デプロイ完了!"
echo ""
echo "📍 アクセス情報:"
echo "   フロントエンド: http://localhost:5173 (開発) / dist/ (本番)"
echo "   バックエンドAPI: http://localhost:8000"
echo "   API文書: http://localhost:8000/docs"
echo ""
echo "🔧 トラブルシューティング:"
echo "   - GPU推論にはNVIDIA GPU (14GB+ VRAM) が必要です"
echo "   - 学習済みモデルファイルが正しく配置されているか確認してください"
echo "   - docker-compose logs rinna-api でログを確認できます"