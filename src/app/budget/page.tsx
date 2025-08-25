'use client'

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, Send, ExternalLink, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function BudgetPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Olá! 👋 Sou especialista em vendas da AllDevs e estou aqui para criar o orçamento PERFEITO para o seu projeto!\n\nAntes de começarmos, me conta: **qual é o seu nome** e **que tipo de projeto você tem em mente?** 🚀\n\n*Pode ser um site, e-commerce, aplicativo, sistema... estou aqui para transformar sua ideia em realidade!*',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showWhatsAppRedirect, setShowWhatsAppRedirect] = useState(false);
  const [whatsappUrl, setWhatsappUrl] = useState('');
  const [sessionId] = useState(() => Date.now().toString()); // Para evitar cache de mensagens antigas
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Filtrar mensagens válidas antes de enviar - só inclui mensagens com content válido
      const validMessages = [...messages, userMessage].filter(msg => {
        return msg && 
               msg.content && 
               typeof msg.content === 'string' && 
               msg.content.trim() !== '' &&
               (msg.role === 'user' || msg.role === 'assistant') &&
               msg.id; // Garantir que tem ID
      });

      console.log('Enviando mensagens válidas:', validMessages);

      const response = await fetch('/api/budget', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: validMessages,
          sessionId: sessionId
        }),
      });

      const data = await response.json();

      if (data.action === 'redirect_whatsapp') {
        setWhatsappUrl(data.whatsappUrl);
        setShowWhatsAppRedirect(true);
      }

      if (data.message) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro. Tente novamente!',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleWhatsAppRedirect = () => {
    window.open(whatsappUrl, '_blank');
  };

  const MessageContent = ({ content }: { content: string }) => (
    <ReactMarkdown
      className="prose prose-invert max-w-none text-sm leading-relaxed"
      components={{
        p: ({ children }) => <p className="text-white/90 mb-2">{children}</p>,
        strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
        em: ({ children }) => <em className="text-purple-300">{children}</em>,
        ul: ({ children }) => <ul className="list-disc list-inside space-y-1 text-white/90">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 text-white/90">{children}</ol>,
        li: ({ children }) => <li className="text-white/90">{children}</li>,
      }}
    >
      {content}
    </ReactMarkdown>
  );

  if (showWhatsAppRedirect) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0A0A1F] via-[#1A1A3F] to-[#2A2A5F] flex items-center justify-center p-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full text-center border border-white/20"
        >
          <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <MessageCircle className="w-8 h-8 text-white" />
          </div>
          
          <h2 className="text-2xl font-bold text-white mb-4">
            Briefing Salvo! 🎉
          </h2>
          
          <p className="text-white/80 mb-6">
            Agora vamos conversar no WhatsApp para finalizar os detalhes do seu projeto!
          </p>
          
          <div className="space-y-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleWhatsAppRedirect}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              <ExternalLink className="w-5 h-5" />
              Abrir WhatsApp
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowWhatsAppRedirect(false)}
              className="w-full bg-white/10 hover:bg-white/20 text-white font-semibold py-3 px-6 rounded-xl transition-colors"
            >
              Continuar Chat
            </motion.button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0A0A1F] via-[#1A1A3F] to-[#2A2A5F]">
      {/* Header */}
      <header className="border-b border-white/10 bg-white/5 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 text-white hover:text-purple-300 transition-colors">
              <ArrowLeft className="w-5 h-5" />
              Voltar
            </Link>
            <h1 className="text-xl font-bold text-white">
              Orçamento AllDevs
            </h1>
            <div className="w-16" /> {/* Spacer */}
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 h-[calc(100vh-200px)] flex flex-col"
        >
          {/* Chat Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                <MessageCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Especialista em Vendas</h3>
                <p className="text-sm text-white/60">AllDevs - Seu parceiro em tecnologia</p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-purple-500 text-white'
                        : 'bg-white/10 text-white border border-white/20'
                    }`}
                  >
                    <MessageContent content={message.content} />
                    <div className="text-xs opacity-60 mt-2">
                      {message.timestamp.toLocaleTimeString('pt-BR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-white/10 border border-white/20 rounded-2xl px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="p-6 border-t border-white/10">
            <div className="flex gap-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite sua mensagem..."
                className="flex-1 bg-white/5 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent"
                disabled={isLoading}
                maxLength={500}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-purple-500 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl transition-colors flex items-center justify-center"
              >
                <Send className="w-5 h-5" />
              </motion.button>
            </div>
          </form>
        </motion.div>
      </div>

      {/* Features Footer */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <MessageCircle className="w-6 h-6 text-purple-400" />
            </div>
            <h4 className="font-semibold text-white mb-2">Consultoria Gratuita</h4>
            <p className="text-sm text-white/60">Análise completa do seu projeto sem custo</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <ExternalLink className="w-6 h-6 text-green-400" />
            </div>
            <h4 className="font-semibold text-white mb-2">Orçamento Inteligente</h4>
            <p className="text-sm text-white/60">Preço calculado com base em horas trabalhadas</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <Send className="w-6 h-6 text-blue-400" />
            </div>
            <h4 className="font-semibold text-white mb-2">Contato Direto</h4>
            <p className="text-sm text-white/60">Conexão imediata via WhatsApp</p>
          </div>
        </div>
      </div>
    </div>
  );
}
