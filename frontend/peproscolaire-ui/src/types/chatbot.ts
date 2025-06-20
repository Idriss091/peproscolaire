export interface ChatbotConversation {
  id: string
  user: string
  user_name?: string
  title?: string
  conversation_type: 'support' | 'academic' | 'administrative' | 'orientation' | 'general'
  status: 'active' | 'closed' | 'archived'
  created_at: string
  updated_at: string
  last_activity: string
  message_count: number
  satisfaction_rating?: number
  messages: ChatbotMessage[]
}

export interface ChatbotMessage {
  id: string
  sender: 'user' | 'bot' | 'system'
  message_type: 'text' | 'quick_reply' | 'attachment' | 'action'
  content: string
  timestamp: string
  is_read: boolean
  intent?: string
  confidence_score?: number
  entities?: any[]
  response_time_ms?: number
}

export interface ChatbotResponse {
  message: string
  message_type: string
  intent?: string
  confidence_score?: number
  entities?: any[]
  quick_replies?: QuickReply[]
  suggestions?: string[]
  needs_human: boolean
  response_time_ms?: number
  tokens_used?: number
}

export interface QuickReply {
  text: string
  action?: string
  payload?: any
}

export interface ChatbotFeedback {
  satisfaction_rating: number
  feedback_text?: string
}

export interface ChatbotSearch {
  query: string
  knowledge_type?: string
  category?: string
  limit?: number
}

export interface ChatbotAction {
  action: string
  payload?: any
}

export interface ChatbotKnowledgeItem {
  id: string
  title: string
  content: string
  knowledge_type: string
  category: string
  similarity_score?: number
}

export interface ChatbotSuggestion {
  title: string
  description: string
  action: string
  type: string
}

export interface ChatbotAnalytics {
  date: string
  total_conversations: number
  new_conversations: number
  total_messages: number
  avg_response_time_ms?: number
  avg_satisfaction_rating?: number
  top_intents: Record<string, number>
}