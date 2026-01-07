export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'user';
  is_admin?: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  message: string;
  // Tokens are now stored in HTTP-only cookies, not in the response
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  message_count: number;
}

export interface ConversationListItem {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message: Message | null;
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
  title?: string;
  deep_dive?: boolean;
}

export interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  ai_response: Message;
  conversation: Conversation;
}

export interface HuggingFaceToken {
  id: number;
  token?: string;
  token_preview?: string;
  name: string;
  is_active: boolean;
  created_by?: number;
  created_by_username?: string;
  assignment_count?: number;
  created_at: string;
  updated_at: string;
}

export interface HuggingFaceTokenCreate {
  token: string;
  name: string;
  is_active?: boolean;
}

export interface HuggingFaceTokenStats {
  total_tokens: number;
  active_tokens: number;
  inactive_tokens: number;
  active_assignments: number;
}

export interface UserHFTokenAssignment {
  id: number;
  user: number;
  user_username: string;
  hf_token: number;
  token_name: string;
  assigned_at: string;
  released_at: string | null;
  is_active: boolean;
  session_identifier: string;
}
