import { create } from 'zustand';
import { apiService } from '@/services/api';
import type { User, LoginCredentials, RegisterData } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiService.login(credentials);
      // Tokens are now stored in HTTP-only cookies by the backend
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Login failed';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    console.log('Register called with data:', data);
    try {
      const response = await apiService.register(data);
      // Tokens are now stored in HTTP-only cookies by the backend
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      // Extract error message from various possible fields
      const errorData = error.response?.data;
      console.error('Registration error:', errorData);
      let errorMessage = 'Registration failed';
      
      if (errorData) {
        if (errorData.username) {
          errorMessage = `Username: ${Array.isArray(errorData.username) ? errorData.username[0] : errorData.username}`;
        } else if (errorData.email) {
          errorMessage = `Email: ${Array.isArray(errorData.email) ? errorData.email[0] : errorData.email}`;
        } else if (errorData.password) {
          errorMessage = `Password: ${Array.isArray(errorData.password) ? errorData.password[0] : errorData.password}`;
        } else if (errorData.password2) {
          errorMessage = `Password confirmation: ${Array.isArray(errorData.password2) ? errorData.password2[0] : errorData.password2}`;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      }
      
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      await apiService.logout();
      // Cookies are cleared by the backend
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({
        user: null,
        isAuthenticated: false,
      });
    }
  },

  loadUser: async () => {
    // Try to load user from cookie-based auth
    set({ isLoading: true });
    try {
      const user = await apiService.getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // No valid token cookie or token expired
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
