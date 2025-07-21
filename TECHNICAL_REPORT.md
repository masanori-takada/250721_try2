# 技術レポート - Rinna-3.6B LoRAファインチューニング

## 🔧 使用技術

### 基盤技術
- **Python 3.x**: メイン開発言語
- **PyTorch**: 深層学習フレームワーク
- **Transformers (Hugging Face)**: 事前学習モデル操作
- **PEFT (Parameter-Efficient Fine-Tuning)**: LoRA実装
- **BitsAndBytes**: モデル量子化
- **Datasets (Hugging Face)**: データセット処理

### モデル・データ
- **ベースモデル**: rinna/japanese-gpt-neox-3.6b (3.6B parameters)
- **データセット**: kunishou/databricks-dolly-15k-ja (15,015件)
- **トークナイザー**: T5Tokenizer (use_fast=False)

### ファインチューニング技術
- **LoRA (Low-Rank Adaptation)**: 効率的パラメータ調整
- **量子化**: 4bit/8bit精度でメモリ効率化
- **勾配蓄積**: 実効バッチサイズ拡大
- **FP16**: 半精度浮動小数点演算

## ⚙️ 作成条件

### ハードウェア環境
```
GPU: NVIDIA A100-SXM4-40GB (39.6GB VRAM)
CPU: Intel/AMD 多コア
RAM: 十分なシステムメモリ
OS: Linux (Ubuntu/CentOS等)
```

### ソフトウェア環境
```
CUDA: 11.8+
Python: 3.8+
PyTorch: 2.0+
Transformers: 4.30+
PEFT: 0.4+
```

### LoRAパラメータ
```
r (rank): 8
alpha: 32
dropout: 0.1
target_modules: ["query_key_value"]
bias: "none"
task_type: "CAUSAL_LM"
```

### 学習パラメータ

#### 従来版
```
batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 1e-4
epochs: 1
quantization: 8bit
warmup_steps: 100
```

#### A100最適化版
```
batch_size: 16
gradient_accumulation_steps: 2
learning_rate: 2e-4
epochs: 1
quantization: 4bit
warmup_steps: 100
dataloader_num_workers: 4
```

### データ処理
```
max_length: 512 tokens
padding: True
truncation: True
preprocessing: プロンプトテンプレート適用
validation_split: なし（全データ学習）
```

## 📊 性能指標

### 学習結果
```
総ステップ数: 470 (最適化版)
学習時間: 9分44秒 (584.28秒)
最終損失: 1.9839
平均損失: 2.039
処理速度: 25.7 samples/sec
```

### リソース使用量
```
VRAM使用量: 18.96GB / 39.6GB (47.8%)
GPU使用率: 100%
消費電力: 369W (最大性能)
学習可能パラメータ: 3.2M (0.09%)
```

### モデルサイズ
```
LoRAアダプタ: 12.9MB
ベースモデル: 7.2GB (量子化済み)
チェックポイント: ~100MB
```

## 🛠️ 実装特徴

### 最適化技術
1. **4bit量子化**: メモリ使用量削減
2. **バッチサイズ最大化**: A100の能力活用
3. **並列データ処理**: 4プロセス並列
4. **勾配蓄積**: 実効バッチサイズ32
5. **fp16精度**: 計算高速化

### プロンプトエンジニアリング
```
### 指示:
{instruction}

### 入力:
{input}

### 回答:
{response}
```

### 推論最適化
```
temperature: 0.7
top_p: 0.75
top_k: 40
no_repeat_ngram_size: 2
max_new_tokens: 256
```

## 📁 成果物構成

### 実行スクリプト
- `rinna_3_6b_lora_training.py`: 記事忠実版
- `rinna_3_6b_lora_training_optimized.py`: A100最適化版
- `rinna_3_6b_inference.py`: テスト付き推論
- `rinna_3_6b_inference_interactive.py`: 対話専用推論

### 学習済みモデル
- `lora-rinna-3.6b-optimized/`: 最適化版LoRAモデル
- `lora-rinna-3.6b-results-optimized/`: 学習ログ・チェックポイント

### 設定・環境
- `requirements.txt`: Python依存関係
- `setup_environment.py`: 環境セットアップ
- `.gitignore`: Git除外設定

## 🎯 技術的成果

### 効率化達成
- **学習ステップ**: 3,754 → 470 (87%削減)
- **バッチサイズ**: 4 → 16 (4倍増加)
- **VRAM活用**: 9GB → 19GB (2倍向上)
- **GPU使用率**: 95% → 100% (最大活用)

### 品質維持
- **損失改善**: 2.737 → 1.984
- **収束安定**: 勾配ノルム0.4-0.6
- **出力品質**: 自然な日本語生成
- **応答速度**: リアルタイム対話可能

## 🔍 参考文献

- **元記事**: [Google Colab で Rinna-3.6B のLoRAファインチューニングを試す](https://note.com/npaka/n/nc387b639e50e)
- **LoRA論文**: "LoRA: Low-Rank Adaptation of Large Language Models"
- **Rinna公式**: [rinna/japanese-gpt-neox-3.6b](https://huggingface.co/rinna/japanese-gpt-neox-3.6b)
- **データセット**: [kunishou/databricks-dolly-15k-ja](https://huggingface.co/datasets/kunishou/databricks-dolly-15k-ja) 