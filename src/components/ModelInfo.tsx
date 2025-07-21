import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info, Cpu, Database, Clock, Target } from 'lucide-react';

export function ModelInfo() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="mx-4 mt-4 bg-white rounded-lg shadow-sm border border-gray-200">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-blue-600" />
          <span className="font-medium text-gray-900">モデル情報</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="flex items-center space-x-3">
              <Cpu className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">モデル</p>
                <p className="text-sm text-gray-600">rinna/japanese-gpt-neox-3.6b</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Database className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">データセット</p>
                <p className="text-sm text-gray-600">databricks-dolly-15k-ja</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Clock className="w-5 h-5 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">学習時間</p>
                <p className="text-sm text-gray-600">9分44秒 (A100最適化)</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Target className="w-5 h-5 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">LoRAサイズ</p>
                <p className="text-sm text-gray-600">12.9MB (0.09%パラメータ)</p>
              </div>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>注意:</strong> これはデモ版です。実際のRinna-3.6Bモデルは大量のVRAM（14GB以上）を必要とするため、
              本格的な利用にはGPU環境での実行が必要です。
            </p>
          </div>
        </div>
      )}
    </div>
  );
}