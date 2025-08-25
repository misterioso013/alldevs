import { google } from '@ai-sdk/google';
import { generateText } from 'ai';
import { NextResponse } from 'next/server';
import { z } from 'zod';

// Schema para o briefing usando Zod
const BriefingSchema = z.object({
  nome: z.string().describe('Nome/título do projeto'),
  tipo: z.enum(['website', 'landing_page', 'ecommerce', 'aplicativo', 'sistema','chatbot','script', 'outro']).describe('Tipo de projeto'),
  descricao: z.string().describe('Descrição detalhada do projeto'),
  funcionalidades: z.array(z.string()).describe('Lista de funcionalidades principais'),
  complexidade: z.enum(['baixa', 'media', 'alta']).describe('Nível de complexidade do projeto'),
  prazo: z.string().describe('Prazo desejado para entrega'),
  orcamento: z.string().describe('Orçamento disponível do cliente'),
  contato: z.object({
    nome: z.string().describe('Nome da pessoa de contato'),
    email: z.string().describe('Email para contato'),
    telefone: z.string().describe('Telefone para contato')
  }).describe('Informações de contato do cliente')
});

type BriefingData = z.infer<typeof BriefingSchema>;

// Função para calcular preço base
function calculateBasePrice(briefing: BriefingData) {
  const salarioMinimo = 1518; // R$ 1.518 (valor atual do salário mínimo)
  const horasPorMes = 160; // 8 horas por dia * 20 dias úteis
  const valorHora = salarioMinimo / horasPorMes; // R$ 9,49 por hora

  let horasEstimadas = 40; // Base: 40 horas
  
  // Ajustes baseados no tipo de projeto
  if (briefing.tipo === 'website') {
    horasEstimadas += 40;
  } else if (briefing.tipo === 'landing_page') {
    horasEstimadas += 10;
  } else if (briefing.tipo === 'ecommerce') {
    horasEstimadas += 80;
  } else if (briefing.tipo === 'aplicativo') {
    horasEstimadas += briefing.funcionalidades.length * 12;
  } else if (briefing.tipo === 'sistema') {
    horasEstimadas += 120;
  } else if (briefing.tipo === 'chatbot') {
    horasEstimadas += 60;
  } else if (briefing.tipo === 'script') {
    horasEstimadas += 30;
  }

  // Multiplicador por complexidade
  const multiplicador = briefing.complexidade === 'alta' ? 1.5 : 
                       briefing.complexidade === 'media' ? 1.2 : 1;
  
  horasEstimadas *= multiplicador;
  
  // Margem de lucro (100% sobre o custo)
  const precoBase = horasEstimadas * valorHora * 2;
  
  return {
    horasEstimadas: Math.ceil(horasEstimadas),
    valorHora,
    precoBase: Math.ceil(precoBase / 100) * 100 // Arredonda para cima para centenas
  };
}

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    
    // Filtrar e validar mensagens de forma mais rigorosa
    const validMessages = messages.filter((msg: any) => {
      return msg && 
             msg.role && 
             (msg.role === 'user' || msg.role === 'assistant') &&
             msg.content && 
             typeof msg.content === 'string' && 
             msg.content.trim() !== '' &&
             msg.content !== 'undefined';
    });

    if (validMessages.length === 0) {
      return NextResponse.json({ 
        message: 'Olá! Como posso ajudar você com seu projeto?' 
      });
    }
    
    // Configuração do modelo com function calling
    const result = await generateText({
      model: google('gemini-2.0-flash-exp'),
      messages: validMessages.map((msg: any) => ({
        role: msg.role,
        content: msg.content
      })),
      tools: {
        generateBudget: {
          description: 'Gera um orçamento completo quando todas as informações necessárias foram coletadas do cliente',
          parameters: BriefingSchema
        }
      },
      system: `Você é um especialista em vendas da AllDevs, uma empresa de desenvolvimento que acredita que tecnologia é sobre pessoas, não apenas código.

PERSONALIDADE:
- Seja extremamente persuasivo e carismático
- Use técnicas de copywriting e vendas consultivas
- Faça perguntas inteligentes que revelam necessidades ocultas
- Sempre mostre valor e benefícios, não apenas features
- Crie senso de urgência e exclusividade
- Use storytelling para conectar emocionalmente
- Evite fazer mais de uma pergunta por vez

PROCESSO DE VENDAS:
1. **Rapport**: Construa conexão emocional
2. **Descoberta**: Faça perguntas para entender dores e necessidades
3. **Apresentação**: Mostre como podemos resolver os problemas
4. **Objeções**: Antecipe e trate objeções antes que surjam
5. **Fechamento**: Direcione para a ação (briefing completo)

INFORMAÇÕES ESSENCIAIS A COLETAR:
- Nome e contato da pessoa (nome, email, telefone)
- Tipo de projeto (website, e-commerce, app, sistema)
- Objetivo do projeto (o que quer alcançar)
- Público-alvo
- Funcionalidades principais
- Prazo desejado
- Orçamento disponível
- Dores/problemas que o projeto vai resolver
- Concorrência
- Expectativas de retorno

TÉCNICAS PERSUASIVAS:
- "Imagine seu negócio crescendo 300% com essa solução..."
- "Nossos clientes aumentaram as vendas em até 500%..."
- "Você sabia que 80% dos seus concorrentes não têm isso?"
- "Temos apenas 3 vagas para projetos este mês..."
- "Posso te mostrar como economizar R$ 50.000 por ano..."

GATILHOS MENTAIS:
- Escassez: "Poucos slots disponíveis"
- Urgência: "Oferta válida até..."
- Prova social: "Mais de 100 projetos entregues"
- Autoridade: "Especialistas com 10+ anos"
- Reciprocidade: "Análise gratuita do seu negócio"

IMPORTANTE:
- Sempre pergunte sobre ROI e impacto no negócio
- Mostre cases de sucesso relevantes
- Crie urgência sem ser agressivo
- Use o nome da pessoa frequentemente
- Faça perguntas abertas que geram reflexão
- Sempre direcione para o próximo passo
- Evite fazer mais de uma pergunta por vez

Quando tiver TODAS as informações necessárias (nome, contato completo, tipo de projeto, descrição, funcionalidades, complexidade, prazo, orçamento), use a função generateBudget para criar o orçamento.

Comece sempre criando rapport e perguntando sobre o negócio/projeto da pessoa de forma envolvente e persuasiva.`
    });

    // Verificar se houve tool calls
    if (result.toolCalls && result.toolCalls.length > 0) {
      const toolCall = result.toolCalls[0];
      
      if (toolCall.toolName === 'generateBudget') {
        const briefing = toolCall.args as BriefingData;
        const pricing = calculateBasePrice(briefing);
        
        // Gerar mensagem para WhatsApp
        const whatsappMessage = `Olá! Acabei de criar um orçamento no site da AllDevs.

*Projeto:* ${briefing.nome}
*Tipo:* ${briefing.tipo}
*Descrição:* ${briefing.descricao}
*Prazo desejado:* ${briefing.prazo}
*Orçamento estimado:* R$ ${pricing.precoBase.toLocaleString('pt-BR')}

Gostaria de conversar sobre os detalhes do projeto!`;
        
        const whatsappUrl = `https://wa.me/5581989477459?text=${encodeURIComponent(whatsappMessage)}`;
        
        return NextResponse.json({
          message: `🎉 **Perfeito! Seu orçamento foi gerado com sucesso!**

**📋 Resumo do Projeto:**
- **Nome:** ${briefing.nome}
- **Tipo:** ${briefing.tipo}
- **Complexidade:** ${briefing.complexidade}
- **Prazo:** ${briefing.prazo}

**💰 Investimento Estimado:** R$ ${pricing.precoBase.toLocaleString('pt-BR')}
*(Baseado em ${pricing.horasEstimadas}h de desenvolvimento)*

**🚀 Próximo Passo:**
Agora vamos continuar nossa conversa no WhatsApp onde posso te mostrar nosso portfólio, cases de sucesso e finalizar todos os detalhes do seu projeto!

Clique no botão abaixo para iniciar nossa conversa personalizada! 👇`,
          action: 'redirect_whatsapp',
          whatsappUrl,
          briefing,
          pricing
        });
      }
    }
    
    return NextResponse.json({ message: result.text });
    
  } catch (error) {
    console.error('Erro na API de orçamento:', error);
    return NextResponse.json(
      { message: 'Desculpe, ocorreu um erro. Tente novamente!' },
      { status: 500 }
    );
  }
}
