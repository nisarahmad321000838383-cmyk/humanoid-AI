import { useEffect, useState } from 'react';
import { useChatStore } from '@/store/chatStore';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import './Chat.css';

const Chat = () => {
  const { loadConversations } = useChatStore();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return (
    <div className="chat-container">
      <Sidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
      <ChatArea isSidebarOpen={isSidebarOpen} onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
    </div>
  );
};

export default Chat;
