/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000/api/v1',
}

export const aiChatConfig = {
  // OpenAI API地址
  apiEndpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',

  // API Key（通过环境变量配置，请勿硬编码到代码中）
  // 在 .env 文件中设置 VITE_DASHSCOPE_API_KEY=your_key_here
  apiKey: import.meta.env.VITE_DASHSCOPE_API_KEY || '',

  // 使用的模型
  model: 'qwen3-max-preview'
}
