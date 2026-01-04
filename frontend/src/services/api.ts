import axios, { AxiosInstance } from 'axios';
import type {
  AuthResponse,
  LoginCredentials,
  RegisterData,
  User,
  Conversation,
  ConversationListItem,
  ChatRequest,
  ChatResponse,
} from '@/types';

const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              const response = await axios.post(
                `${API_BASE_URL}/auth/token/refresh/`,
                { refresh: refreshToken }
              );
              const { access } = response.data;
              localStorage.setItem('accessToken', access);
              originalRequest.headers.Authorization = `Bearer ${access}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/register/', data);
    return response.data;
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/login/', credentials);
    return response.data;
  }

  async logout(refreshToken: string): Promise<void> {
    await this.api.post('/auth/logout/', { refresh_token: refreshToken });
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me/');
    return response.data;
  }

  // Chat endpoints
  async getConversations(): Promise<ConversationListItem[]> {
    const response = await this.api.get<any>('/chat/conversations/');
    // Handle paginated response from DRF
    if (response.data && typeof response.data === 'object' && 'results' in response.data) {
      return response.data.results;
    }
    // Handle non-paginated response (array)
    return Array.isArray(response.data) ? response.data : [];
  }

  async getConversation(id: number): Promise<Conversation> {
    const response = await this.api.get<Conversation>(`/chat/conversations/${id}/`);
    return response.data;
  }

  async deleteConversation(id: number): Promise<void> {
    await this.api.delete(`/chat/conversations/${id}/`);
  }

  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await this.api.post<ChatResponse>('/chat/chat/', data);
    return response.data;
  }
}

export const apiService = new ApiService();
