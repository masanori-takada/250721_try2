import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Github, ExternalLink, AlertCircle, CheckCircle } from 'lucide-react';
import { ChatMessage } from './components/ChatMessage';
import { ModelInfo } from './components/ModelInfo';
import { rinnaAPI } from './services/api';
import { mockRinnaAPI } from './services/mockAPI';
import type { Message } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'こんにちは！Rinna-3.6B対話システムです。何でもお気軽にお聞きください。',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [useRealAPI, setUseRealAPI] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // API状態チェック
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const isOnline = await rinnaAPI.healthCheck();
        setApiStatus(isOnline ? 'online' : 'offline');
        setUseRealAPI(isOnline);
      } catch (error) {
        setApiStatus('offline');
        setUseRealAPI(false);
      }
    };

    checkAPI();
    // 30秒ごとにAPI状態をチェック
    const interval = setInterval(checkAPI, 30000);
    return () => clearInterval(interval);
  }, []);
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      let response: string;
      
      if (useRealAPI && apiStatus === 'online') {
        // 実際のRinna-3.6B APIを使用
        const apiResponse = await rinnaAPI.chat({
          message: input.trim(),
          max_tokens: 256,
          temperature: 0.7,
          top_p: 0.75,
          top_k: 40
        });
        response = apiResponse.response;
      } else {
        // モックAPIを使用
        response = await mockRinnaAPI(input.trim());
      }
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'すみません、エラーが発生しました。もう一度お試しください。',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto max-w-4xl h-screen flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Rinna-3.6B 対話システム</h1>
                <div className="flex items-center space-x-2">
                  <p className="text-sm text-gray-600">日本語特化型AI対話モデル</p>
                  <div className="flex items-center space-x-1">
                    {apiStatus === 'checking' && (
                      <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
                    )}
                    {apiStatus === 'online' && (
                      <>
                        <CheckCircle className="w-3 h-3 text-green-500" />
                        <span className="text-xs text-green-600">実モデル</span>
                      </>
                    )}
                    {apiStatus === 'offline' && (
                      <>
                        <AlertCircle className="w-3 h-3 text-orange-500" />
                        <span className="text-xs text-orange-600">デモ版</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <a
              href="https://github.com/masanori-takada/250721_try2"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-3 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm">GitHub</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </header>

        {/* Model Info */}
        <ModelInfo apiStatus={apiStatus} useRealAPI={useRealAPI} />

        {/* Chat Area */}
        <div className="flex-1 overflow-hidden flex flex-col bg-white mx-4 rounded-t-lg shadow-lg">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center space-x-2 text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">
                  {useRealAPI ? 'Rinna-3.6Bが考え中...' : '考え中...'}
                </span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-3">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="メッセージを入力してください..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={1}
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                  disabled={isLoading}
                />
              </div>
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Enter で送信、Shift + Enter で改行
            </p>
            {apiStatus === 'offline' && (
              <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded text-xs text-orange-700">
                💡 実際のRinna-3.6Bモデルが利用できません。デモ版で動作中です。
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="p-4 text-center text-sm text-gray-600">
          <p>
            参考: <a 
              href="https://note.com/npaka/n/nc387b639e50e" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Google Colab で Rinna-3.6B のLoRAファインチューニングを試す
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;