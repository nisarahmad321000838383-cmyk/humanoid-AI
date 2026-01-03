import { useState, useRef, useEffect, FormEvent } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';
import { Send, Menu, Sparkles, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './ChatArea.css';

interface ChatAreaProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

const ChatArea = ({ isSidebarOpen, onToggleSidebar }: ChatAreaProps) => {
  const { user } = useAuthStore();
  const { currentConversation, sendMessage, isSending, error } = useChatStore();
  const [input, setInput] = useState('');
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
      await sendMessage(message, currentConversation?.id);
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
      </div>

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
                onClick={() => setInput('What is quantum computing?')}
              >
                What is quantum computing?
              </button>
              <button
                className="example-prompt"
                onClick={() => setInput('Explain machine learning in simple terms')}
              >
                Explain machine learning
              </button>
              <button
                className="example-prompt"
                onClick={() => setInput('How does blockchain work?')}
              >
                How does blockchain work?
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
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              {...props}
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
        <form onSubmit={handleSubmit} className="chat-input-form">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything..."
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
