#!/usr/bin/env python3
"""
Rinna-3.6B LoRA対話システム - FastAPI Backend
学習済みLoRAモデルを使用した本格的なAPI
"""

import os
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# パラメータ
MODEL_NAME = "rinna/japanese-gpt-neox-3.6b"
PEFT_NAME = "lora-rinna-3.6b-optimized"

app = FastAPI(title="Rinna-3.6B Chat API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数
model = None
tokenizer = None

class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.75
    top_k: int = 40

class ChatResponse(BaseModel):
    response: str
    status: str
    model_info: dict

def load_model():
    """モデルとトークナイザーの読み込み"""
    global model, tokenizer
    
    try:
        logger.info("モデル読み込み開始...")
        
        # トークナイザーの準備
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
        logger.info("トークナイザー読み込み完了")
        
        # ベースモデルの準備
        base_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            load_in_8bit=True,
            device_map="auto",
            torch_dtype=torch.float16
        )
        logger.info("ベースモデル読み込み完了")
        
        # LoRAモデルの適用
        if os.path.exists(PEFT_NAME):
            model = PeftModel.from_pretrained(
                base_model, 
                PEFT_NAME, 
                device_map="auto"
            )
            logger.info(f"LoRAモデル {PEFT_NAME} 読み込み完了")
        else:
            model = base_model
            logger.warning(f"LoRAモデル {PEFT_NAME} が見つかりません。ベースモデルを使用します。")
        
        # 評価モード
        model.eval()
        logger.info("モデル準備完了")
        
    except Exception as e:
        logger.error(f"モデル読み込みエラー: {e}")
        raise

def generate_prompt(instruction, input_text=None):
    """プロンプトテンプレートの生成"""
    if input_text:
        result = f"""### 指示:
{instruction}

### 入力:
{input_text}

### 回答:
"""
    else:
        result = f"""### 指示:
{instruction}

### 回答:
"""
    
    # 改行→<NL>
    result = result.replace('\n', '<NL>')
    return result

def generate_response(instruction, input_text=None, max_tokens=256, temperature=0.7, top_p=0.75, top_k=40):
    """テキスト生成"""
    try:
        # プロンプト生成
        prompt = generate_prompt(instruction, input_text)
        
        # トークナイズ
        input_ids = tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            add_special_tokens=False
        ).input_ids.cuda()
        
        # 生成
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids, 
                max_new_tokens=max_tokens, 
                do_sample=True,
                temperature=temperature, 
                top_p=top_p, 
                top_k=top_k,         
                no_repeat_ngram_size=2,
                pad_token_id=tokenizer.eos_token_id
            )
        
        outputs = outputs[0].tolist()
        
        # EOSトークンでデコード完了
        if tokenizer.eos_token_id in outputs:
            eos_index = outputs.index(tokenizer.eos_token_id)
            decoded = tokenizer.decode(outputs[:eos_index])
            
            # レスポンス内容のみ抽出
            sentinel = "### 回答:"
            sentinel_loc = decoded.find(sentinel)
            if sentinel_loc >= 0:
                result = decoded[sentinel_loc + len(sentinel):].strip()
                # <NL>→改行
                result = result.replace("<NL>", "\n")
                return result
            else:
                return "申し訳ありません。適切な応答を生成できませんでした。"
        else:
            return "申し訳ありません。応答の生成が完了しませんでした。"
            
    except Exception as e:
        logger.error(f"生成エラー: {e}")
        return f"エラーが発生しました: {str(e)}"

@app.on_event("startup")
async def startup_event():
    """アプリ起動時の処理"""
    logger.info("Rinna-3.6B Chat API 起動中...")
    load_model()
    logger.info("API準備完了")

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "message": "Rinna-3.6B Chat API",
        "status": "running",
        "model": MODEL_NAME,
        "lora": PEFT_NAME
    }

@app.get("/model-info")
async def model_info():
    """モデル情報"""
    return {
        "base_model": MODEL_NAME,
        "lora_model": PEFT_NAME,
        "parameters": "3.6B",
        "lora_size": "12.9MB",
        "training_data": "databricks-dolly-15k-ja",
        "training_time": "9分44秒",
        "gpu_required": "14GB+ VRAM"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """対話エンドポイント"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="モデルが読み込まれていません")
    
    try:
        # 応答生成
        response = generate_response(
            instruction=request.message,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k
        )
        
        return ChatResponse(
            response=response,
            status="success",
            model_info={
                "model": MODEL_NAME,
                "lora": PEFT_NAME,
                "parameters_used": {
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "top_k": request.top_k
                }
            }
        )
        
    except Exception as e:
        logger.error(f"チャットエラー: {e}")
        raise HTTPException(status_code=500, detail=f"応答生成エラー: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )