FROM nvidia/cuda:11.8-devel-ubuntu20.04

# 環境変数
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# Python依存関係のインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# LoRAモデルのダウンロード（GitHubから）
RUN mkdir -p lora-rinna-3.6b-optimized
# 実際の運用では、学習済みモデルファイルをここに配置

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["python3", "app.py"]