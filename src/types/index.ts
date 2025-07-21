export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export interface ModelConfig {
  name: string;
  version: string;
  parameters: string;
  dataset: string;
  trainingTime: string;
  accuracy: string;
}