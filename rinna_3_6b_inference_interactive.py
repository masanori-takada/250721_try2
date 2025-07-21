#!/usr/bin/env python3
"""
Rinna-3.6B LoRAモデル推論実装（対話専用版）
参考: https://note.com/npaka/n/nc387b639e50e
"""

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# パラメータ
model_name = "rinna/japanese-gpt-neox-3.6b"
peft_name = "lora-rinna-3.6b-optimized"  # 最適化版のパスに修正

def prepare_model_and_tokenizer():
    """モデルとトークナイザーの準備"""
    print("=== モデルとトークナイザーの準備 ===")
    
    # モデルの準備
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_8bit=True,
        device_map="auto",
    )
    
    # トークナイザーの準備
    # Rinnaのトークナイザーでは use_fast=False が必要
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    
    # LoRAモデルの準備
    model = PeftModel.from_pretrained(
        model, 
        peft_name, 
        device_map="auto"
    )
    
    # 評価モード
    model.eval()
    
    print("モデルとトークナイザーの準備完了")
    return model, tokenizer

def generate_prompt(data_point):
    """プロンプトテンプレートの準備（推論用：レスポンス内容なし版）"""
    if data_point["input"]:
        result = f"""### 指示:
{data_point["instruction"]}

### 入力:
{data_point["input"]}

### 回答:
"""
    else:
        result = f"""### 指示:
{data_point["instruction"]}

### 回答:
"""

    # 改行→<NL>
    result = result.replace('\n', '<NL>')
    return result

def generate(model, tokenizer, instruction, input=None, maxTokens=256):
    """テキスト生成関数"""
    # 推論
    prompt = generate_prompt({'instruction': instruction, 'input': input})
    
    # Rinnaのtokenizer()は自動でEOSが追加されるため add_special_tokens=False を指定
    input_ids = tokenizer(prompt, 
        return_tensors="pt", 
        truncation=True, 
        add_special_tokens=False).input_ids.cuda()
    
    outputs = model.generate(
        input_ids=input_ids, 
        max_new_tokens=maxTokens, 
        do_sample=True,
        temperature=0.7, 
        top_p=0.75, 
        top_k=40,         
        no_repeat_ngram_size=2,
    )
    outputs = outputs[0].tolist()

    # EOSトークンにヒットしたらデコード完了
    if tokenizer.eos_token_id in outputs:
        eos_index = outputs.index(tokenizer.eos_token_id)
        decoded = tokenizer.decode(outputs[:eos_index])

        # レスポンス内容のみ抽出
        sentinel = "### 回答:"
        sentinelLoc = decoded.find(sentinel)
        if sentinelLoc >= 0:
            result = decoded[sentinelLoc+len(sentinel):]
            print("\n回答:")
            print(result.replace("<NL>", "\n"))  # <NL>→改行
            return result.replace("<NL>", "\n")
        else:
            print('Warning: Expected prompt template to be emitted. Ignoring output.')
            return None
    else:
        print('Warning: no <eos> detected ignoring output')
        return None

def interactive_chat(model, tokenizer):
    """対話モード"""
    print("\n=== 対話モード ===")
    print("質問を入力してください（'quit'で終了）:")
    
    while True:
        try:
            question = input("\n質問: ")
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n対話を終了します")
                break
            
            print("\n考え中...")
            generate(model, tokenizer, question)
            
        except KeyboardInterrupt:
            print("\n対話を終了します")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")

def main():
    """メイン処理"""
    print("Rinna-3.6B LoRAモデル推論（対話専用版）")
    print("参考: https://note.com/npaka/n/nc387b639e50e")
    print("=" * 50)
    
    try:
        # モデルとトークナイザーの準備
        model, tokenizer = prepare_model_and_tokenizer()
        
        # 対話モード（テストをスキップ）
        interactive_chat(model, tokenizer)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("LoRAモデルが存在しない可能性があります。")
        print("先に rinna_3_6b_lora_training.py を実行してください。")

if __name__ == "__main__":
    main() 