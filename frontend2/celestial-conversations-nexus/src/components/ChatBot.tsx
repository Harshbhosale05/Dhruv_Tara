
import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Satellite, Earth, Moon, Sun, Rocket, Radio, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { apiClient, API_BASE_URL } from '@/config/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const ChatBot = () => {
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: '1',
      text: "🚀 Greetings from Dhruv_Tara Mission Control! I'm your advanced space exploration assistant. How can I help you explore the cosmos today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = React.useState('');
  const [isTyping, setIsTyping] = React.useState(false);
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentQuery = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    try {
      // Send query to backend API
      console.log('Sending query to backend:', currentQuery);
      
      const data = await apiClient.chat(currentQuery);
      console.log('Backend response:', data);
      
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || "I'm sorry, I couldn't process your request. Please try again.",
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Show detailed error message to user
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: `🚨 **Connection Error**\n\nCouldn't reach Mission Control at ${API_BASE_URL}\n\n**Details:** ${errorMessage}\n\n**Troubleshooting:**\n• Ensure the backend server is running\n• Check if the API is accessible at ${API_BASE_URL}/chat\n• Verify CORS settings allow requests from this frontend`,
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: any) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  React.useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <Card className="w-full max-w-4xl bg-card/90 backdrop-blur-xl border-primary/30 space-glow relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary/10 via-transparent to-purple-500/10"></div>
      </div>
      
      <div className="relative p-6">
        {/* Enhanced Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Satellite className="w-10 h-10 text-primary satellite-float satellite-glow" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full pulse-glow"></div>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-gradient">Dhruv_Tara Mission Control</h2>
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Activity className="w-3 h-3 text-green-400" />
                Your gateway to space exploration • Online
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 text-xs text-muted-foreground bg-primary/10 px-3 py-1 rounded-full">
              <Radio className="w-3 h-3" />
              <span>Live</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground bg-green-400/10 px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Connected</span>
            </div>
          </div>
        </div>
        
        {/* Enhanced Chat Area */}
        <ScrollArea className="h-96 pr-4 mb-6" ref={scrollAreaRef}>
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-6 py-4 relative ${
                    message.sender === 'user'
                      ? 'bg-primary text-primary-foreground ml-4 rounded-tr-sm'
                      : 'bg-secondary/90 text-secondary-foreground mr-4 rounded-tl-sm border border-primary/20'
                  }`}
                >
                  {message.sender === 'bot' && (
                    <div className="flex items-center gap-3 mb-3">
                      <div className="relative">
                        <Earth className="w-5 h-5 text-primary orbital-animation" style={{animationDuration: '8s'}} />
                        <div className="absolute inset-0 bg-primary/20 rounded-full blur-sm"></div>
                      </div>
                      <span className="text-sm font-semibold text-primary">Dhruv_Tara Mission Control</span>
                      <div className="flex-1 h-px bg-gradient-to-r from-primary/50 to-transparent"></div>
                    </div>
                  )}
                  <div className="text-sm leading-relaxed">
                    {message.sender === 'user' ? (
                      message.text
                    ) : (
                      <div className="prose prose-sm prose-invert max-w-none">
                        <ReactMarkdown>
                          {message.text}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center justify-between mt-3">
                    <p className="text-xs opacity-70">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                    {message.sender === 'bot' && (
                      <div className="flex items-center gap-1">
                        <Rocket className="w-3 h-3 opacity-50" />
                        <span className="text-xs opacity-50">Verified</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-secondary/90 text-secondary-foreground rounded-2xl px-6 py-4 mr-4 rounded-tl-sm border border-primary/20">
                  <div className="flex items-center gap-3 mb-3">
                    <Earth className="w-5 h-5 text-primary" />
                    <span className="text-sm font-semibold text-primary">Dhruv_Tara Mission Control</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-xs text-muted-foreground">Processing mission data...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        {/* Enhanced Input Area */}
        <div className="space-y-4">
          <div className="flex gap-3">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about Dhruv_Tara missions, satellites, launches, or space exploration..."
              className="flex-1 bg-input/70 border-primary/40 focus:border-primary/80 text-foreground placeholder:text-muted-foreground/60 h-12 px-4 rounded-lg backdrop-blur-sm"
              disabled={isTyping}
            />
            <Button 
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className="bg-primary hover:bg-primary/90 text-primary-foreground space-glow h-12 px-6 rounded-lg font-semibold"
            >
              <Satellite className="w-4 h-4 mr-2 satellite-spin" />
              {isTyping ? 'Processing...' : 'Launch'}
            </Button>
          </div>
          
          {/* Status Bar */}
          <div className="flex items-center justify-between text-xs text-muted-foreground bg-primary/5 px-4 py-2 rounded-lg border border-primary/10">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full pulse-glow"></div>
                <span>Mission Control Online</span>
              </div>
              <div className="flex items-center gap-2">
                <Moon className="w-3 h-3" />
                <span>Lunar Operations Active</span>
              </div>
              <div className="flex items-center gap-2">
                <Sun className="w-3 h-3 text-yellow-400" />
                <span>Solar Array Tracking</span>
              </div>
            </div>
            <div className="text-primary/80 font-mono">
              {messages.length - 1} messages • {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ChatBot;
