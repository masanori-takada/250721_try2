#!/usr/bin/env python3
"""
Rinna-3.6B LoRAファインチューニング実装
参考: https://note.com/npaka/n/nc387b639e50e

注意: Google Colab Pro/Pro+ の A100で動作確認。VRAMは14.0GB必要。
"""

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType
)

# 基本パラメータ
model_name = "rinna/japanese-gpt-neox-3.6b"
dataset = "kunishou/databricks-dolly-15k-ja"
peft_name = "lora-rinna-3.6b"
output_dir = "lora-rinna-3.6b-results"

CUTOFF_LEN = 256  # コンテキスト長

def setup_environment():
    """環境セットアップ"""
    print("=== 環境セットアップ ===")
    
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
    
    # Rinnaのトークナイザーでは use_fast=False が必要
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    
    # スペシャルトークンの確認
    print("スペシャルトークン:")
    print(tokenizer.special_tokens_map)
    print(f"bos_token : {tokenizer.bos_token} , {tokenizer.bos_token_id}")
    print(f"eos_token : {tokenizer.eos_token} , {tokenizer.eos_token_id}")
    print(f"unk_token : {tokenizer.unk_token} , {tokenizer.unk_token_id}")
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
    
    # データの確認
    print("\nデータサンプル:")
    print(data["train"][5])
    
    # トークナイズの動作確認
    test_tokenize = tokenize("hi there", tokenizer)
    print(f"\nトークナイズテスト: {test_tokenize}")
    
    # プロンプト生成の確認
    test_prompt = generate_prompt(data["train"][0])
    print(f"\nプロンプトテスト: {test_prompt[:200]}...")
    
    def generate_and_tokenize_prompt(data_point):
        full_prompt = generate_prompt(data_point)
        return tokenize(full_prompt, tokenizer)
    
    # データセットの変換
    train_data = data["train"].map(generate_and_tokenize_prompt)
    
    return train_data

def prepare_model():
    """モデルの準備"""
    print("\n=== モデルの準備 ===")
    
    # モデルの読み込み
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_8bit=True,
        device_map="auto",
    )
    
    # LoRAの設定
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.1,
    )
    
    # PEFTモデルの適用
    model = get_peft_model(model, peft_config)
    
    # 学習可能パラメータの確認
    model.print_trainable_parameters()
    
    return model

def train_model(model, tokenizer, train_data):
    """モデルの学習"""
    print("\n=== モデルの学習 ===")
    
    # 学習パラメータの設定
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=1,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=1,
        warmup_steps=100,
        logging_steps=20,
        save_steps=200,
        eval_steps=200,
        save_total_limit=3,
        learning_rate=1e-4,
        fp16=True,
        report_to="none",  # W&Bを無効化
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
    
    # キャッシュを無効化して学習開始
    model.config.use_cache = False
    trainer.train()
    model.config.use_cache = True
    
    # LoRAモデルの保存
    trainer.model.save_pretrained(peft_name)
    
    print(f"LoRAモデルを {peft_name} に保存しました")

def main():
    """メイン処理"""
    print("Rinna-3.6B LoRAファインチューニング開始")
    print("参考: https://note.com/npaka/n/nc387b639e50e")
    print("=" * 50)
    
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
    
    print("\n=== 学習完了 ===")
    print(f"LoRAモデル: {peft_name}")
    print(f"学習結果: {output_dir}")

if __name__ == "__main__":
    main() 