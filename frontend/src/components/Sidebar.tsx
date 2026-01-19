import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useChatStore } from '@/store/chatStore';
import {
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  MessageSquare,
  Trash2,
  LogOut,
  Sparkles,
  User,
  Shield,
  Settings as SettingsIcon,
  Loader2,
} from 'lucide-react';
import './Sidebar.css';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar = ({ isOpen, onToggle }: SidebarProps) => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const {
    conversations,
    currentConversation,
    createNewConversation,
    loadConversation,
    deleteConversation,
    loadMoreConversations,
    hasMore,
    isLoading,
  } = useChatStore();
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const lastConversationRef = useCallback((node: HTMLDivElement | null) => {
    if (isLoading) return;
    if (observerRef.current) observerRef.current.disconnect();
    
    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        loadMoreConversations();
      }
    });
    
    if (node) observerRef.current.observe(node);
  }, [isLoading, hasMore, loadMoreConversations]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleDeleteConversation = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      setDeletingId(id);
      await deleteConversation(id);
      setDeletingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <Sparkles size={24} />
            {isOpen && (
              <div className="sidebar-logo-text">
                <h2>Humanoid AI</h2>
                <span>No Hallucination</span>
              </div>
            )}
          </div>
          <button className="toggle-button" onClick={onToggle} title="Toggle sidebar">
            {isOpen ? <PanelLeftClose size={20} /> : <PanelLeftOpen size={20} />}
          </button>
        </div>

        <div className="sidebar-content">
          <button
            className="new-chat-button"
            onClick={createNewConversation}
            title="New conversation"
          >
            <Plus size={20} />
            {isOpen && <span>New Conversation</span>}
          </button>

          <div className="conversations-list">
            {conversations.map((conv, index) => {
              // Attach ref to the last conversation item for infinite scroll
              const isLastItem = index === conversations.length - 1;
              
              return (
                <div
                  key={conv.id}
                  ref={isLastItem ? lastConversationRef : null}
                  className={`conversation-item ${
                    currentConversation?.id === conv.id ? 'active' : ''
                  }`}
                  onClick={() => loadConversation(conv.id)}
                >
                  <div className="conversation-icon">
                    <MessageSquare size={18} />
                  </div>
                  {isOpen && (
                    <>
                      <div className="conversation-content">
                        <div className="conversation-title">{conv.title}</div>
                        <div className="conversation-date">{formatDate(conv.updated_at)}</div>
                      </div>
                      <button
                        className="delete-button"
                        onClick={(e) => handleDeleteConversation(conv.id, e)}
                        disabled={deletingId === conv.id}
                        title="Delete conversation"
                      >
                        <Trash2 size={16} />
                      </button>
                    </>
                  )}
                </div>
              );
            })}
            
            {/* Loading indicator when fetching more conversations */}
            {isLoading && hasMore && (
              <div className="loading-more">
                <Loader2 size={20} className="spinner" />
                {isOpen && <span>Loading more...</span>}
              </div>
            )}
            
            {/* End of list message */}
            {!hasMore && conversations.length > 0 && isOpen && (
              <div className="end-of-list">
                <span>No more conversations</span>
              </div>
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          {user && (
            <div className="user-info">
              <div className="user-avatar">
                {user.role === 'admin' ? <Shield size={18} /> : <User size={18} />}
              </div>
              {isOpen && (
                <div className="user-details">
                  <div className="user-name">{user.username}</div>
                  <div className="user-role">{user.role}</div>
                </div>
              )}
            </div>
          )}
          {(user?.is_admin || user?.role === 'admin') && (
            <button 
              className="settings-button" 
              onClick={() => navigate('/settings')} 
              title="Settings"
            >
              <SettingsIcon size={20} />
              {isOpen && <span>Settings</span>}
            </button>
          )}
          <button className="logout-button" onClick={handleLogout} title="Logout">
            <LogOut size={20} />
            {isOpen && <span>Logout</span>}
          </button>
        </div>
      </div>
      {isOpen && <div className="sidebar-overlay" onClick={onToggle} />}
    </>
  );
};

export default Sidebar;
