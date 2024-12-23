'use client'

import { useChat } from 'ai/react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useRef, useState, ComponentPropsWithoutRef } from 'react';
import { Pin, PinOff, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import type { Components } from 'react-markdown';

export default function ChatComponent() {
  const [isPinned, setIsPinned] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    initialMessages: [
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Olá! Sou o assistente da AllDevs. Como posso ajudar você hoje?'
      }
    ]
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (messages.length > 1) {
      scrollToBottom();
    }
  }, [messages]);

  const handleCopyCode = async (code: string) => {
    await navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const MessageContent = ({ content }: { content: string }) => (
    <ReactMarkdown
      rehypePlugins={[rehypeHighlight]}
      className="prose prose-invert max-w-none prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10"
      components={{
        // Customização dos elementos markdown
        p: ({ children }) => <p className="text-sm sm:text-base text-white/90">{children}</p>,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" 
             className="text-purple-400 hover:text-purple-300 underline">
            {children}
          </a>
        ),
        code: ({ className, children, inline, ...props }: ComponentPropsWithoutRef<'code'> & { inline?: boolean }) => {
          const code = String(children).replace(/\n$/, '');
          
          return !inline ? (
            <div className="relative group">
              <pre className="rounded-lg p-4 bg-black/50 border border-white/10 overflow-x-auto">
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => handleCopyCode(code)}
                  className="absolute right-2 top-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 
                           transition-colors border border-white/10"
                >
                  {copiedCode === code ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4 text-white/70" />
                  )}
                </motion.button>
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            </div>
          ) : (
            <code className="bg-white/10 rounded px-1 py-0.5" {...props}>
              {children}
            </code>
          );
        },
        ul: ({ children }) => <ul className="list-disc list-inside space-y-1 text-white/90">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 text-white/90">{children}</ol>,
        li: ({ children }) => <li className="text-sm sm:text-base">{children}</li>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-purple-500 pl-4 italic text-white/70">
            {children}
          </blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );

  if (isPinned) {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-[#0A0A1F]"
      >
        <div className="h-full flex flex-col">
          {/* Header do Chat */}
          <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
            <h3 className="text-white font-medium">Chat AllDevs</h3>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsPinned(false)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Modo normal"
            >
              <PinOff className="w-5 h-5 text-white/70" />
            </motion.button>
          </div>

          {/* Container de Mensagens */}
          <div className="flex-1 overflow-y-auto p-4 messages-container">
            <AnimatePresence mode="popLayout">
              {messages.map(message => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={`flex ${message.role === 'assistant' ? 'justify-start' : 'justify-end'} mb-4`}
                >
                  <div
                    className={`
                      max-w-[85%] sm:max-w-[80%] rounded-xl p-3 sm:p-4
                      ${message.role === 'assistant' 
                        ? 'bg-white/10 text-white' 
                        : 'bg-purple-500/20 text-white ml-auto'}
                    `}
                  >
                    <MessageContent content={message.content} />
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

          {/* Formulário de Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-white/10 bg-white/5">
            <div className="flex gap-2 max-w-4xl mx-auto">
              <input
                value={input}
                onChange={handleInputChange}
                placeholder="Digite sua mensagem..."
                className="flex-1 bg-white/5 rounded-xl px-4 py-2 text-white placeholder-white/50 
                         focus:outline-none focus:ring-2 focus:ring-purple-500/50
                         text-sm sm:text-base"
                disabled={isLoading}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={isLoading}
                className="glass-button-primary w-auto px-6 py-2"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto" />
                ) : (
                  'Enviar'
                )}
              </motion.button>
            </div>
          </form>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl relative"
    >
      {/* Header do Chat */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <h3 className="text-white font-medium">Chat AllDevs</h3>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsPinned(true)}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title="Modo tela cheia"
        >
          <Pin className="w-5 h-5 text-white/70" />
        </motion.button>
      </div>

      {/* Container de Mensagens */}
      <div className="h-[400px] overflow-y-auto p-4 messages-container">
        <AnimatePresence mode="popLayout">
          {messages.map(message => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`flex ${message.role === 'assistant' ? 'justify-start' : 'justify-end'} mb-4`}
            >
              <div
                className={`
                  max-w-[85%] sm:max-w-[80%] rounded-xl p-3 sm:p-4
                  ${message.role === 'assistant' 
                    ? 'bg-white/10 text-white' 
                    : 'bg-purple-500/20 text-white ml-auto'}
                `}
              >
                <MessageContent content={message.content} />
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Formulário de Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Digite sua mensagem..."
            className="flex-1 bg-white/5 rounded-xl px-4 py-2 text-white placeholder-white/50 
                     focus:outline-none focus:ring-2 focus:ring-purple-500/50
                     text-sm sm:text-base"
            disabled={isLoading}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={isLoading}
            className="glass-button-primary w-full sm:w-auto px-6 py-2"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto" />
            ) : (
              'Enviar'
            )}
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
} 