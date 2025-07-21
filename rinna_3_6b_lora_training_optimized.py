#!/usr/bin/env python3
"""
Rinna-3.6B LoRAファインチューニング実装 - A100最適化版
参考: https://note.com/npaka/n/nc387b639e50e
"""

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType
)

# 基本パラメータ（最適化版）
model_name = "rinna/japanese-gpt-neox-3.6b"
dataset = "kunishou/databricks-dolly-15k-ja"
peft_name = "lora-rinna-3.6b-optimized"
output_dir = "lora-rinna-3.6b-results-optimized"

CUTOFF_LEN = 256  # コンテキスト長

def setup_environment():
    """環境セットアップ"""
    print("=== A100最適化版環境セットアップ ===")
    
    # 作業フォルダの作成
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(peft_name, exist_ok=True)
    
    print(f"モデル名: {model_name}")
    print(f"データセット: {dataset}")
    print(f"PEFTフォルダ: {peft_name}")
    print(f"出力フォルダ: {output_dir}")

def prepare_tokenizer():
    """トークナイザーの準備"""
    print("\n=== トークナイザーの準備 ===")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    
    # スペシャルトークンの確認
    print("スペシャルトークン:")
    print(f"bos_token : {tokenizer.bos_token} , {tokenizer.bos_token_id}")
    print(f"eos_token : {tokenizer.eos_token} , {tokenizer.eos_token_id}")
    print(f"pad_token : {tokenizer.pad_token} , {tokenizer.pad_token_id}")
    
    return tokenizer

def tokenize(prompt, tokenizer):
    """トークナイズ関数"""
    result = tokenizer(
        prompt,
        truncation=True,
        max_length=CUTOFF_LEN,
        padding=False,
    )
    return {
        "input_ids": result["input_ids"],
        "attention_mask": result["attention_mask"],
    }

def generate_prompt(data_point):
    """プロンプトテンプレートの準備"""
    if data_point["input"]:
        result = f"""### 指示:
{data_point["instruction"]}

### 入力:
{data_point["input"]}

### 回答:
{data_point["output"]}"""
    else:
        result = f"""### 指示:
{data_point["instruction"]}

### 回答:
{data_point["output"]}"""
    
    # 改行→<NL>
    result = result.replace('\n', '<NL>')
    return result

def prepare_dataset(tokenizer):
    """データセットの準備"""
    print("\n=== データセットの準備 ===")
    
    # データセットの読み込み
    data = load_dataset(dataset)
    print(f"データセットサイズ: {len(data['train'])}")
    
    def generate_and_tokenize_prompt(data_point):
        full_prompt = generate_prompt(data_point)
        return tokenize(full_prompt, tokenizer)
    
    # データセットの変換（並列処理で高速化）
    train_data = data["train"].map(
        generate_and_tokenize_prompt,
        num_proc=4,  # 並列処理
        remove_columns=data["train"].column_names
    )
    
    return train_data

def prepare_model():
    """モデルの準備 - A100最適化版"""
    print("\n=== A100最適化モデルの準備 ===")
    
    # A100向け最適化された量子化設定
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,  # 4bit量子化でメモリ効率向上
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    # モデルの読み込み
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    
    # A100向け最適化されたLoRA設定
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,  # 安定した値に戻す
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["query_key_value"]  # 基本的なターゲットに戻す
    )
    
    # PEFTモデルの適用
    model = get_peft_model(model, peft_config)
    
    # 学習可能パラメータの確認
    model.print_trainable_parameters()
    
    return model

def train_model(model, tokenizer, train_data):
    """A100最適化モデルの学習"""
    print("\n=== A100最適化学習 ===")
    
    # A100向け最適化された学習パラメータ
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=1,
        per_device_train_batch_size=16,  # バッチサイズを4倍に増加
        gradient_accumulation_steps=2,   # 勾配蓄積でさらに効果的なバッチサイズに
        warmup_steps=100,
        logging_steps=10,  # ログ頻度を上げる
        save_steps=500,
        eval_steps=500,
        save_total_limit=3,
        learning_rate=2e-4,  # 学習率を上げる
        fp16=True,
        dataloader_num_workers=4,  # データローダー並列化
        remove_unused_columns=False,
        report_to="none",
        gradient_checkpointing=False,  # 勾配エラー回避のため無効化
        optim="adamw_torch",  # 安定したオプティマイザー
    )
    
    # データコレクターの準備
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # トレーナーの準備
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        data_collator=data_collator,
    )
    
    # 学習実行
    print("🚀 A100最適化学習開始...")
    model.config.use_cache = False
    trainer.train()
    model.config.use_cache = True
    
    # LoRAモデルの保存
    trainer.model.save_pretrained(peft_name)
    
    print(f"✅ A100最適化LoRAモデルを {peft_name} に保存しました")

def main():
    """メイン処理"""
    print("🚀 Rinna-3.6B LoRAファインチューニング - A100最適化版")
    print("参考: https://note.com/npaka/n/nc387b639e50e")
    print("=" * 60)
    
    # GPU情報の表示
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    
    # 環境セットアップ
    setup_environment()
    
    # トークナイザーの準備
    tokenizer = prepare_tokenizer()
    
    # データセットの準備
    train_data = prepare_dataset(tokenizer)
    
    # モデルの準備
    model = prepare_model()
    
    # 学習の実行
    train_model(model, tokenizer, train_data)
    
    print("\n🎉 A100最適化学習完了 🎉")
    print(f"LoRAモデル: {peft_name}")
    print(f"学習結果: {output_dir}")

if __name__ == "__main__":
    main() 