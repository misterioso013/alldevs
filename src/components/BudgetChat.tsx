'use client'

import { useChat } from 'ai/react';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useRef, useState, ComponentPropsWithoutRef } from 'react';
import { Pin, PinOff, Copy, Check, ExternalLink, DollarSign } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

interface BudgetData {
  projectName: string;
  projectType: string;
  description: string;
  features: string[];
  timeline: string;
  budget: string;
  contactInfo: {
    name: string;
    email: string;
    phone: string;
    company?: string;
  };
  additionalInfo: string;
  estimatedPrice: number;
  estimatedHours: number;
}

export default function BudgetChat() {
  const [isPinned, setIsPinned] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [budgetData, setBudgetData] = useState<BudgetData | null>(null);
  const [showBudgetSummary, setShowBudgetSummary] = useState(false);
  const [whatsappUrl, setWhatsappUrl] = useState<string>('');
  
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/budget',
    initialMessages: [
      {
        id: 'welcome',
        role: 'assistant',
        content: `🚀 **Olá! Sou seu consultor de projetos da AllDevs!**

Estou aqui para transformar sua ideia em um projeto incrível! 💡

Vou te fazer algumas perguntas estratégicas para entender exatamente o que você precisa. Meu objetivo é criar o briefing perfeito e te apresentar uma proposta que vai superar suas expectativas!

**Vamos começar?** Me conte: qual é a sua ideia de projeto? 🎯`
      }
    ],
    onFinish: (message) => {
      // Verificar se a mensagem indica que o orçamento foi gerado
      if (message.content.includes('Perfeito! Seu orçamento foi gerado') || 
          message.content.includes('Próximo Passo') ||
          message.content.includes('WhatsApp')) {
        setShowBudgetSummary(true);
      }

      // Verificar se a mensagem contém dados do orçamento (método legado)
      const budgetMatch = message.content.match(/BUDGET_DATA:\s*(\{.*\})/s);
      if (budgetMatch) {
        try {
          const budget = JSON.parse(budgetMatch[1]);
          setBudgetData(budget);
          setShowBudgetSummary(true);
        } catch (error) {
          console.error('Erro ao parsear dados do orçamento:', error);
        }
      }
    }
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

  const handleWhatsAppRedirect = () => {
    if (whatsappUrl) {
      window.open(whatsappUrl, '_blank');
      return;
    }

    if (!budgetData) return;
    
    const message = `Olá! Acabei de fazer um orçamento no site da AllDevs para o projeto "${budgetData.projectName}". 

*Resumo do Projeto:*
- Tipo: ${budgetData.projectType}
- Prazo: ${budgetData.timeline}
- Orçamento estimado: R$ ${budgetData.estimatedPrice.toLocaleString('pt-BR')}

Gostaria de conversar sobre os detalhes! 🚀`;

    const fallbackWhatsappUrl = `https://wa.me/5511999999999?text=${encodeURIComponent(message)}`;
    window.open(fallbackWhatsappUrl, '_blank');
  };

  // Custom handleSubmit para interceptar respostas da API
  const customHandleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    try {
      const response = await fetch('/api/budget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          messages: [...messages, { 
            id: Date.now().toString(),
            role: 'user', 
            content: input.trim() 
          }] 
        })
      });

      const data = await response.json();
      
      // Verificar se a resposta contém redirecionamento para WhatsApp
      if (data.action === 'redirect_whatsapp') {
        setWhatsappUrl(data.whatsappUrl);
        setBudgetData(data.briefing);
        setShowBudgetSummary(true);
        
        // Adicionar a mensagem do usuário e do assistente manualmente
        const userMessage = {
          id: Date.now().toString(),
          role: 'user' as const,
          content: input.trim()
        };
        
        const assistantMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant' as const,
          content: data.message
        };

        // Usar o método interno do useChat para adicionar mensagens
        handleSubmit(e);
        return;
      }
      
      // Se não há redirecionamento, usar o handleSubmit padrão
      handleSubmit(e);
      
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      // Em caso de erro, usar o handleSubmit padrão
      handleSubmit(e);
    }
  };

  const MessageContent = ({ content }: { content: string }) => {
    // Filtrar dados do orçamento da exibição
    const cleanContent = content.replace(/BUDGET_DATA:\s*\{[\s\S]*?\}/g, '').trim();
    
    return (
      <ReactMarkdown
        rehypePlugins={[rehypeHighlight]}
        className="prose prose-invert max-w-none prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10"
        components={{
          p: ({ children }) => <p className="text-sm sm:text-base text-white/90 mb-3">{children}</p>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" 
               className="text-purple-400 hover:text-purple-300 underline">
              {children}
            </a>
          ),
          code: ({ className, children, inline, ...props }: ComponentPropsWithoutRef<'code'> & { inline?: boolean }) => {
            const code = String(children).replace(/\n$/, '');
            const isInline = inline || !className?.includes('language-');
            
            return isInline ? (
              <code className="bg-white/10 rounded px-1 py-0.5 text-purple-300 font-mono text-sm" {...props}>
                {children}
              </code>
            ) : (
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
            );
          },
          ul: ({ children }) => <ul className="list-disc list-inside space-y-1 text-white/90 mb-3">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 text-white/90 mb-3">{children}</ol>,
          li: ({ children }) => <li className="text-sm sm:text-base">{children}</li>,
          strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
          em: ({ children }) => <em className="text-purple-300">{children}</em>,
          h1: ({ children }) => <h1 className="text-2xl font-bold text-white mb-4">{children}</h1>,
          h2: ({ children }) => <h2 className="text-xl font-bold text-white mb-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-lg font-bold text-white mb-2">{children}</h3>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-purple-500 pl-4 italic text-white/70 my-4">
              {children}
            </blockquote>
          ),
        }}
      >
        {cleanContent}
      </ReactMarkdown>
    );
  };

  const BudgetSummary = () => {
    if (!budgetData) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-effect rounded-xl p-6 mb-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <DollarSign className="w-6 h-6 text-green-400" />
          <h3 className="text-xl font-bold text-white">Resumo do Orçamento</h3>
        </div>
        
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="space-y-2">
            <p className="text-white/70"><strong>Projeto:</strong> {budgetData.projectName}</p>
            <p className="text-white/70"><strong>Tipo:</strong> {budgetData.projectType}</p>
            <p className="text-white/70"><strong>Prazo:</strong> {budgetData.timeline}</p>
          </div>
          <div className="space-y-2">
            <p className="text-white/70"><strong>Horas estimadas:</strong> {budgetData.estimatedHours}h</p>
            <p className="text-white/70"><strong>Valor estimado:</strong> <span className="text-green-400 font-bold">R$ {budgetData.estimatedPrice.toLocaleString('pt-BR')}</span></p>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="text-white font-semibold mb-2">Funcionalidades:</h4>
          <ul className="list-disc list-inside text-white/70 space-y-1">
            {budgetData.features.map((feature, index) => (
              <li key={index}>{feature}</li>
            ))}
          </ul>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleWhatsAppRedirect}
          className="w-full glass-button-primary py-3 flex items-center justify-center gap-2"
        >
          <ExternalLink className="w-5 h-5" />
          Continuar no WhatsApp
        </motion.button>
      </motion.div>
    );
  };

  if (isPinned) {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-[#0A0A1F]"
      >
        <div className="h-full flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
            <h3 className="text-white font-medium">Orçamento AllDevs</h3>
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

          <div className="flex-1 overflow-y-auto p-4 messages-container">
            {showBudgetSummary && <BudgetSummary />}
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

          <form onSubmit={customHandleSubmit} className="p-4 border-t border-white/10 bg-white/5">
            <div className="flex gap-2 max-w-4xl mx-auto">
              <input
                value={input}
                onChange={handleInputChange}
                placeholder="Digite sua resposta..."
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
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <h3 className="text-white font-medium">Consultor de Projetos</h3>
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

      <div className="h-[500px] overflow-y-auto p-4 messages-container">
        {showBudgetSummary && <BudgetSummary />}
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

      <form onSubmit={customHandleSubmit} className="p-4 border-t border-white/10">
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Digite sua resposta..."
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
