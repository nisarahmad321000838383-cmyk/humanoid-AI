import { create } from 'zustand';
import { apiService } from '@/services/api';
import type { Conversation, ConversationListItem } from '@/types';

interface ChatState {
  conversations: ConversationListItem[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  loadConversations: () => Promise<void>;
  loadConversation: (id: number) => Promise<void>;
  sendMessage: (message: string, conversationId?: number) => Promise<void>;
  deleteConversation: (id: number) => Promise<void>;
  createNewConversation: () => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  isLoading: false,
  isSending: false,
  error: null,

  loadConversations: async () => {
    set({ isLoading: true, error: null });
    try {
      const conversations = await apiService.getConversations();
      set({ conversations, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to load conversations',
        isLoading: false,
      });
    }
  },

  loadConversation: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const conversation = await apiService.getConversation(id);
      set({ currentConversation: conversation, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to load conversation',
        isLoading: false,
      });
    }
  },

  sendMessage: async (message, conversationId) => {
    set({ isSending: true, error: null });
    try {
      const response = await apiService.sendMessage({
        message,
        conversation_id: conversationId,
        title: conversationId ? undefined : message.slice(0, 50),
      });

      set({
        currentConversation: response.conversation,
        isSending: false,
      });

      // Reload conversations list
      get().loadConversations();
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to send message',
        isSending: false,
      });
      throw error;
    }
  },

  deleteConversation: async (id) => {
    try {
      await apiService.deleteConversation(id);
      const conversations = get().conversations.filter((c) => c.id !== id);
      set({ conversations });
      
      if (get().currentConversation?.id === id) {
        set({ currentConversation: null });
      }
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to delete conversation',
      });
    }
  },

  createNewConversation: () => {
    set({ currentConversation: null });
  },

  clearError: () => set({ error: null }),
}));
