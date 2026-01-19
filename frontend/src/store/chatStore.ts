import { create } from 'zustand';
import { apiService } from '@/services/api';
import type { Conversation, ConversationListItem, Product } from '@/types';

interface ChatState {
  conversations: ConversationListItem[];
  currentConversation: Conversation | null;
  relevantProducts: Product[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  currentPage: number;
  hasMore: boolean;
  totalCount: number;
  loadConversations: (page?: number) => Promise<void>;
  loadMoreConversations: () => Promise<void>;
  loadConversation: (id: number) => Promise<void>;
  sendMessage: (message: string, conversationId?: number, deepDive?: boolean) => Promise<void>;
  deleteConversation: (id: number) => Promise<void>;
  createNewConversation: () => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  relevantProducts: [],
  isLoading: false,
  isSending: false,
  error: null,
  currentPage: 1,
  hasMore: true,
  totalCount: 0,

  loadConversations: async (page = 1) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.getConversations(page);
      set({ 
        conversations: response.results, 
        currentPage: page,
        hasMore: response.next !== null,
        totalCount: response.count,
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to load conversations',
        isLoading: false,
      });
    }
  },

  loadMoreConversations: async () => {
    const { currentPage, hasMore, isLoading, conversations } = get();
    
    if (!hasMore || isLoading) return;
    
    set({ isLoading: true, error: null });
    try {
      const nextPage = currentPage + 1;
      const response = await apiService.getConversations(nextPage);
      set({ 
        conversations: [...conversations, ...response.results],
        currentPage: nextPage,
        hasMore: response.next !== null,
        totalCount: response.count,
        isLoading: false 
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to load more conversations',
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

  sendMessage: async (message, conversationId, deepDive = false) => {
    set({ isSending: true, error: null });
    try {
      const response = await apiService.sendMessage({
        message,
        conversation_id: conversationId,
        title: conversationId ? undefined : message.slice(0, 50),
        deep_dive: deepDive,
      });

      set({
        currentConversation: response.conversation,
        relevantProducts: response.relevant_products || [],
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
