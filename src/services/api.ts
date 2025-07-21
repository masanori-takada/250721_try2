// 実際のRinna-3.6B APIクライアント
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
}

export interface ChatResponse {
  response: string;
  status: string;
  model_info: {
    model: string;
    lora: string;
    parameters_used: {
      max_tokens: number;
      temperature: number;
      top_p: number;
      top_k: number;
    };
  };
}

export interface ModelInfo {
  base_model: string;
  lora_model: string;
  parameters: string;
  lora_size: string;
  training_data: string;
  training_time: string;
  gpu_required: string;
}

class RinnaAPI {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/`);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  async getModelInfo(): Promise<ModelInfo> {
    const response = await fetch(`${this.baseURL}/model-info`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: request.message,
        max_tokens: request.max_tokens || 256,
        temperature: request.temperature || 0.7,
        top_p: request.top_p || 0.75,
        top_k: request.top_k || 40,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

export const rinnaAPI = new RinnaAPI();