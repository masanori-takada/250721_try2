# Rinna-3.6B 対話システム Web版

[元のGitHubリポジトリ](https://github.com/masanori-takada/250721_try2)のRinna-3.6B LoRAファインチューニングプロジェクトをベースにしたWeb対話アプリケーションです。

## 概要

このアプリケーションは、Rinna-3.6B日本語言語モデルをLoRAファインチューニングした対話システムのWebインターフェースです。実際のモデルは大量のVRAM（14GB以上）を必要とするため、このデモ版ではモックAPIを使用して動作を再現しています。

## 特徴

- 🤖 **日本語特化**: Rinna-3.6Bベースの日本語対話AI
- 💬 **リアルタイム対話**: スムーズなチャットインターフェース
- 📱 **レスポンシブ**: モバイル・デスクトップ対応
- ⚡ **高速**: Vite + React + TypeScript
- 🎨 **モダンUI**: Tailwind CSS + Lucide Icons

## 技術スタック

- **フロントエンド**: React 18 + TypeScript
- **スタイリング**: Tailwind CSS
- **アイコン**: Lucide React
- **ビルドツール**: Vite
- **元モデル**: rinna/japanese-gpt-neox-3.6b

## 開発・デプロイ

### ローカル開発

```bash
npm install
npm run dev
```

### ビルド

```bash
npm run build
```

### プレビュー

```bash
npm run preview
```

## 実際のモデル使用について

このWebアプリはデモ版です。実際のRinna-3.6Bモデルを使用するには：

1. **GPU環境**: NVIDIA A100など高性能GPU（VRAM 14GB以上）
2. **元リポジトリ**: [masanori-takada/250721_try2](https://github.com/masanori-takada/250721_try2)
3. **実行スクリプト**: `rinna_3_6b_inference_interactive.py`

## モデル情報

- **ベースモデル**: rinna/japanese-gpt-neox-3.6b
- **ファインチューニング**: LoRA (r=8, alpha=32)
- **データセット**: databricks-dolly-15k-ja (15,015件)
- **学習時間**: 9分44秒 (A100最適化版)
- **モデルサイズ**: 12.9MB (LoRAアダプタ)

## 参考文献

- [元記事: Google Colab で Rinna-3.6B のLoRAファインチューニングを試す](https://note.com/npaka/n/nc387b639e50e)
- [Rinna-3.6B モデル](https://huggingface.co/rinna/japanese-gpt-neox-3.6b)
- [元GitHubリポジトリ](https://github.com/masanori-takada/250721_try2)

## ライセンス

このプロジェクトは元リポジトリの実装に基づいており、学習・研究目的で使用してください。