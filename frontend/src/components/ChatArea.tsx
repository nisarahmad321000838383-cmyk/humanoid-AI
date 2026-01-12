import { useState, useRef, useEffect, FormEvent } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';
import { Send, Menu, Sparkles, Loader2, Brain, Briefcase } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import BusinessModal from './BusinessModal';
import ProductCard from './ProductCard';
import './ChatArea.css';

interface ChatAreaProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

const ChatArea = ({ isSidebarOpen, onToggleSidebar }: ChatAreaProps) => {
  const { user } = useAuthStore();
  const { currentConversation, relevantProducts, sendMessage, isSending, error } = useChatStore();
  const [input, setInput] = useState('');
  const [deepDive, setDeepDive] = useState(false);
  const [isBusinessModalOpen, setIsBusinessModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    const message = input.trim();
    setInput('');

    try {
      await sendMessage(message, currentConversation?.id, deepDive);
    } catch (error) {
      // Error handled by store
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="chat-area">
      <div className="chat-header">
        {!isSidebarOpen && (
          <button className="menu-button" onClick={onToggleSidebar}>
            <Menu size={20} />
          </button>
        )}
        <div className="chat-header-content">
          <h1>Humanoid AI</h1>
          <span className="chat-slogan">No Hallucination</span>
        </div>
        <button 
          className="business-button" 
          onClick={() => setIsBusinessModalOpen(true)}
          title="Manage your business"
        >
          <Briefcase size={20} />
          <span>Your Business</span>
        </button>
      </div>

      <BusinessModal 
        isOpen={isBusinessModalOpen} 
        onClose={() => setIsBusinessModalOpen(false)} 
      />

      <div className="chat-messages">
        {!currentConversation?.messages?.length ? (
          <div className="empty-state">
            <Sparkles size={64} className="empty-icon" />
            <h2>Welcome to Humanoid AI</h2>
            <p>
              Ask me anything. I'm designed with the core principle of "No Hallucination" -
              providing accurate, reliable responses without making up information.
            </p>
            <div className="example-prompts">
              <button
                className="example-prompt"
                onClick={() => setInput('I need a Laptop!')}
              >
                I need a Laptop!
              </button>
              <button
                className="example-prompt"
                onClick={() => setInput('I want to buy a Smartphone!')}
              >
                I want to buy a Smartphone!
              </button>
              <button
                className="example-prompt"
                onClick={() => setInput('tell me what is computer programming?')}
              >
                I want to learn programming!
              </button>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {currentConversation.messages.map((message, index) => (
              <div key={message.id || index} className={`message ${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' ? (
                    <span>{user?.username.charAt(0).toUpperCase()}</span>
                  ) : (
                    <Sparkles size={18} />
                  )}
                </div>
                <div className="message-content">
                  <div className="message-role">
                    {message.role === 'user' ? user?.username : 'Humanoid AI'}
                  </div>
                  <div className="message-text">
                    <ReactMarkdown
                      components={{
                        code({ className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          const isInline = !match;
                          return !isInline ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus as any}
                              language={match ? match[1] : 'text'}
                              PreTag="div"
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                  
                  {/* Show product cards after the last AI message if products are available */}
                  {message.role === 'assistant' && 
                   index === currentConversation.messages.length - 1 && 
                   relevantProducts.length > 0 && (
                    <div className="products-container">
                      <div className="products-grid">
                        {relevantProducts.map((product) => (
                          <ProductCard key={product.id} product={product} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isSending && (
              <div className="message assistant">
                <div className="message-avatar">
                  <Sparkles size={18} />
                </div>
                <div className="message-content">
                  <div className="message-role">Humanoid AI</div>
                  <div className="message-text">
                    <Loader2 className="spinner" size={20} />
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {error && (
        <div className="chat-error">
          <span>{error}</span>
        </div>
      )}

      <div className="chat-input-container">
        <div className="chat-options">
          <button
            type="button"
            className={`deep-dive-toggle ${deepDive ? 'active' : ''}`}
            onClick={() => setDeepDive(!deepDive)}
            title={deepDive ? 'Deep Dive Mode: ON - Detailed, thoughtful responses' : 'Deep Dive Mode: OFF - Quick, concise responses'}
          >
            <Brain size={18} />
            <span>Deep Dive</span>
            {deepDive && <span className="deep-dive-indicator">ON</span>}
          </button>
        </div>
        <form onSubmit={handleSubmit} className="chat-input-form">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={deepDive ? "Ask for a detailed, thoughtful analysis..." : "Ask me anything..."}
            rows={1}
            disabled={isSending}
          />
          <button type="submit" disabled={!input.trim() || isSending}>
            {isSending ? <Loader2 className="spinner" size={20} /> : <Send size={20} />}
          </button>
        </form>
        <p className="chat-disclaimer">
          Humanoid AI may make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
};

export default ChatArea;
