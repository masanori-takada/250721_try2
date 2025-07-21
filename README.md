# Rinna-3.6B LoRAファインチューニング

[Google Colab で Rinna-3.6B のLoRAファインチューニングを試す](https://note.com/npaka/n/nc387b639e50e) の記事に忠実に実装したPythonスクリプト集です。

## 概要

**Rinna-3.6B** は、Rinna社が開発した日本語に特化した36億パラメータのGPT言語モデルです。商用利用可能なライセンスで公開されており、このモデルをベースにLoRAファインチューニングを行うことで、対話型AI等の開発が可能です。

## 必要環境

⚠️ **重要**: この実装は大量のVRAMを必要とします

- **推奨環境**: Google Colab Pro/Pro+ A100
- **必要VRAM**: 14.0GB以上
- **Python**: 3.8以上
- **CUDA対応GPU**

## ファイル構成

```
250721_try2/
├── README.md                      # このファイル
├── requirements.txt               # 依存関係
├── setup_environment.py          # 環境セットアップ
├── rinna_3_6b_lora_training.py   # LoRAファインチューニング
└── rinna_3_6b_inference.py       # 推論・対話
```

## 使用方法

### 1. 環境セットアップ

```bash
# 環境セットアップの実行
python setup_environment.py
```

または手動でセットアップ:

```bash
# PEFTの最新版インストール
pip install -Uqq git+https://github.com/huggingface/peft.git

# 必要なライブラリのインストール
pip install -Uqq transformers datasets accelerate bitsandbytes sentencepiece
```

### 2. LoRAファインチューニングの実行

```bash
python rinna_3_6b_lora_training.py
```

**学習パラメータ:**
- モデル: `rinna/japanese-gpt-neox-3.6b`
- データセット: `kunishou/databricks-dolly-15k-ja`
- コンテキスト長: 256
- エポック数: 1
- バッチサイズ: 4

### 3. 推論・対話の実行

```bash
python rinna_3_6b_inference.py
```

## 実装の特徴

### プロンプトテンプレート

```
### 指示:
{instruction}

### 入力:
{input}

### 回答:
{output}
```

### LoRA設定

- **r**: 8
- **lora_alpha**: 32
- **lora_dropout**: 0.1
- **task_type**: CAUSAL_LM

### トークナイザーの注意点

Rinnaのトークナイザーでは以下の設定が必要:
- `use_fast=False`
- 推論時に `add_special_tokens=False`

## テスト例

記事と同じテスト質問を実行します:

```python
# テスト質問例
questions = [
    "自然言語処理とは？",
    "日本の首都は？", 
    "まどか☆マギカで一番かわいいのは？"
]
```

**期待される出力例:**
- 自然言語処理 → 人間が日常的に使っている自然な言語を理解し...
- 日本の首都 → 東京は、日本の首都です。
- まどか☆マギカ → 暁美ほむらは、まどかマミの親友であり...

## トラブルシューティング

### VRAMが不足する場合

1. バッチサイズを削減
2. より小さなモデルを使用
3. 勾配チェックポイントを有効化

### 学習が進まない場合

1. 学習率の調整
2. ウォームアップステップの調整
3. データセットの確認

## 参考リンク

- [元記事: Google Colab で Rinna-3.6B のLoRAファインチューニングを試す](https://note.com/npaka/n/nc387b639e50e)
- [Rinna-3.6B モデル](https://huggingface.co/rinna/japanese-gpt-neox-3.6b)
- [データセット](https://huggingface.co/datasets/kunishou/databricks-dolly-15k-ja)
- [PEFT Documentation](https://huggingface.co/docs/peft/)

## ライセンス

このコードは元記事の実装に基づいており、学習・研究目的で使用してください。
Rinna-3.6Bモデル自体は商用利用可能なライセンスです。

---

**作成者**: 記事実装版  
**参考**: [npaka氏のnote記事](https://note.com/npaka/n/nc387b639e50e) 