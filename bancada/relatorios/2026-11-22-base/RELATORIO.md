# Relatório da bancada

Base: http://127.0.0.1:8765 — 15 páginas — gerado em 2026-11-22T15:10:58.496Z

## Resumo

| Meta | Resultado | Falhas |
|---|---|---|
| Capturas em 430 e 1440 px | PASSA | 0/15 páginas |
| axe: zero problemas serious/critical | FALHA | 15/15 páginas |
| Sem JS: título, contato e (em /projetos/) todos os cards | PASSA | 0/15 páginas |
| Sem rolagem horizontal em 430 px | PASSA | 0/15 páginas |
| Links internos respondem 200, sem redirecionamento | PASSA | 0/15 páginas |
| reducedMotion: nenhum transform após 1 s | FALHA | 7/15 páginas |
| Lighthouse móvel: LCP < 2500 ms e CLS < 0,05 | FALHA | 4/15 páginas |

Código de saída: **1**

## Capturas em 430 e 1440 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | home-430.png, home-1440.png |
| /caio/ | passa | caio-430.png, caio-1440.png |
| /historia.html | passa | historia.html-430.png, historia.html-1440.png |
| /projetos/ | passa | projetos-430.png, projetos-1440.png |
| /projetos/fakly/ | passa | projetos_fakly-430.png, projetos_fakly-1440.png |
| /projetos/heisuca/ | passa | projetos_heisuca-430.png, projetos_heisuca-1440.png |
| /projetos/prosup/ | passa | projetos_prosup-430.png, projetos_prosup-1440.png |
| /projetos/sendany/ | passa | projetos_sendany-430.png, projetos_sendany-1440.png |
| /rosiel/ | passa | rosiel-430.png, rosiel-1440.png |
| /servicos/aplicativo-mobile-react-native/ | passa | servicos_aplicativo-mobile-react-native-430.png, servicos_aplicativo-mobile-react-native-1440.png |
| /servicos/automacoes-integracoes-api/ | passa | servicos_automacoes-integracoes-api-430.png, servicos_automacoes-integracoes-api-1440.png |
| /servicos/bots-whatsapp-automacao/ | passa | servicos_bots-whatsapp-automacao-430.png, servicos_bots-whatsapp-automacao-1440.png |
| /servicos/criacao-de-sites-institucionais/ | passa | servicos_criacao-de-sites-institucionais-430.png, servicos_criacao-de-sites-institucionais-1440.png |
| /servicos/desenvolvimento-mvp-startups/ | passa | servicos_desenvolvimento-mvp-startups-430.png, servicos_desenvolvimento-mvp-startups-1440.png |
| /servicos/landing-page-conversao/ | passa | servicos_landing-page-conversao-430.png, servicos_landing-page-conversao-1440.png |

## axe: zero problemas serious/critical

| Página | Resultado | Detalhe |
|---|---|---|
| / | FALHA | color-contrast (serious, 27, 430 px); color-contrast (serious, 27, 1440 px) |
| /caio/ | FALHA | color-contrast (serious, 15, 430 px); color-contrast (serious, 15, 1440 px) |
| /historia.html | FALHA | color-contrast (serious, 28, 430 px); color-contrast (serious, 28, 1440 px) |
| /projetos/ | FALHA | color-contrast (serious, 18, 430 px); color-contrast (serious, 18, 1440 px) |
| /projetos/fakly/ | FALHA | color-contrast (serious, 14, 430 px); color-contrast (serious, 14, 1440 px) |
| /projetos/heisuca/ | FALHA | color-contrast (serious, 14, 430 px); color-contrast (serious, 14, 1440 px) |
| /projetos/prosup/ | FALHA | color-contrast (serious, 14, 430 px); color-contrast (serious, 14, 1440 px) |
| /projetos/sendany/ | FALHA | color-contrast (serious, 14, 430 px); color-contrast (serious, 14, 1440 px) |
| /rosiel/ | FALHA | color-contrast (serious, 18, 430 px); color-contrast (serious, 18, 1440 px) |
| /servicos/aplicativo-mobile-react-native/ | FALHA | color-contrast (serious, 4, 430 px); color-contrast (serious, 5, 1440 px) |
| /servicos/automacoes-integracoes-api/ | FALHA | color-contrast (serious, 4, 430 px); color-contrast (serious, 5, 1440 px) |
| /servicos/bots-whatsapp-automacao/ | FALHA | color-contrast (serious, 4, 430 px); color-contrast (serious, 5, 1440 px) |
| /servicos/criacao-de-sites-institucionais/ | FALHA | color-contrast (serious, 4, 430 px); color-contrast (serious, 5, 1440 px) |
| /servicos/desenvolvimento-mvp-startups/ | FALHA | color-contrast (serious, 4, 430 px); color-contrast (serious, 5, 1440 px) |
| /servicos/landing-page-conversao/ | FALHA | color-contrast (serious, 4, 430 px); color-contrast (serious, 5, 1440 px) |

## Sem JS: título, contato e (em /projetos/) todos os cards

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | h1 "Fazemos software que vive.", contatos visíveis 3/3 |
| /caio/ | passa | h1 "Caio Guerras", contatos visíveis 3/3 |
| /historia.html | passa | h1 "Uma históriafora do roteiro", contatos visíveis 3/3 |
| /projetos/ | passa | h1 "Projetos", contatos visíveis 3/3, cards visíveis 4/4 |
| /projetos/fakly/ | passa | h1 "Fakly", contatos visíveis 3/3 |
| /projetos/heisuca/ | passa | h1 "Heisuca", contatos visíveis 3/3 |
| /projetos/prosup/ | passa | h1 "ProsUp", contatos visíveis 3/3 |
| /projetos/sendany/ | passa | h1 "SendAny", contatos visíveis 3/3 |
| /rosiel/ | passa | h1 "Rosiel Victor", contatos visíveis 3/3 |
| /servicos/aplicativo-mobile-react-native/ | passa | h1 "Desenvolvimento de Aplicativo Mobile iOS e Android com React Native", contatos visíveis 3/3 |
| /servicos/automacoes-integracoes-api/ | passa | h1 "Automação de Processos e Integração de Sistemas via API e Webhook", contatos visíveis 3/3 |
| /servicos/bots-whatsapp-automacao/ | passa | h1 "Bot para WhatsApp, Discord e Telegram — Automação de Atendimento 24h", contatos visíveis 3/3 |
| /servicos/criacao-de-sites-institucionais/ | passa | h1 "Criação de Site Institucional Profissional para Empresas", contatos visíveis 3/3 |
| /servicos/desenvolvimento-mvp-startups/ | passa | h1 "Desenvolvimento de MVP Web para Startups — Do Zero ao Ar em Semanas", contatos visíveis 3/3 |
| /servicos/landing-page-conversao/ | passa | h1 "Landing Page de Alta Conversão com Integração WhatsApp", contatos visíveis 3/3 |

## Sem rolagem horizontal em 430 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | scrollWidth 430 / clientWidth 430 |
| /caio/ | passa | scrollWidth 430 / clientWidth 430 |
| /historia.html | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/fakly/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/heisuca/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/prosup/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/sendany/ | passa | scrollWidth 430 / clientWidth 430 |
| /rosiel/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/aplicativo-mobile-react-native/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/automacoes-integracoes-api/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/bots-whatsapp-automacao/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/criacao-de-sites-institucionais/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/desenvolvimento-mvp-startups/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/landing-page-conversao/ | passa | scrollWidth 430 / clientWidth 430 |

## Links internos respondem 200, sem redirecionamento

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 19 ok |
| /caio/ | passa | 15 ok |
| /historia.html | passa | 12 ok |
| /projetos/ | passa | 17 ok |
| /projetos/fakly/ | passa | 14 ok |
| /projetos/heisuca/ | passa | 14 ok |
| /projetos/prosup/ | passa | 14 ok |
| /projetos/sendany/ | passa | 14 ok |
| /rosiel/ | passa | 17 ok |
| /servicos/aplicativo-mobile-react-native/ | passa | 19 ok |
| /servicos/automacoes-integracoes-api/ | passa | 18 ok |
| /servicos/bots-whatsapp-automacao/ | passa | 17 ok |
| /servicos/criacao-de-sites-institucionais/ | passa | 18 ok |
| /servicos/desenvolvimento-mvp-startups/ | passa | 19 ok |
| /servicos/landing-page-conversao/ | passa | 17 ok |

## reducedMotion: nenhum transform após 1 s

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | nenhum |
| /caio/ | passa | nenhum |
| /historia.html | FALHA | 12: div#hk.hist-kicker = matrix(1, 0, 0, 1, 0, 0); h1#ht.hist-title = matrix(1, 0, 0, 1, 0, 0.0015); p#hs.hist-sub = matrix(1, 0, 0, 1, 0, 0.7043); div.tl-content.reveal = matrix(1, 0, 0, 1, 0, 40); div.tl-content.reveal = matrix(1, 0, 0, 1, 0, 40) |
| /projetos/ | passa | nenhum |
| /projetos/fakly/ | passa | nenhum |
| /projetos/heisuca/ | passa | nenhum |
| /projetos/prosup/ | passa | nenhum |
| /projetos/sendany/ | passa | nenhum |
| /rosiel/ | passa | nenhum |
| /servicos/aplicativo-mobile-react-native/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/automacoes-integracoes-api/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/bots-whatsapp-automacao/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/criacao-de-sites-institucionais/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/desenvolvimento-mvp-startups/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/landing-page-conversao/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |

## Lighthouse móvel: LCP < 2500 ms e CLS < 0,05

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | LCP 1381 ms, CLS 0.038 |
| /caio/ | FALHA | LCP 2587 ms, CLS 0.007 |
| /historia.html | passa | LCP 1888 ms, CLS 0.015 |
| /projetos/ | passa | LCP 1373 ms, CLS 0.000 |
| /projetos/fakly/ | passa | LCP 1370 ms, CLS 0.000 |
| /projetos/heisuca/ | passa | LCP 1371 ms, CLS 0.000 |
| /projetos/prosup/ | passa | LCP 1371 ms, CLS 0.001 |
| /projetos/sendany/ | passa | LCP 1373 ms, CLS 0.000 |
| /rosiel/ | FALHA | LCP 3152 ms, CLS 0.007 |
| /servicos/aplicativo-mobile-react-native/ | passa | LCP 1834 ms, CLS 0.000 |
| /servicos/automacoes-integracoes-api/ | FALHA | LCP 2738 ms, CLS 0.000 |
| /servicos/bots-whatsapp-automacao/ | passa | LCP 1834 ms, CLS 0.000 |
| /servicos/criacao-de-sites-institucionais/ | passa | LCP 1835 ms, CLS 0.048 |
| /servicos/desenvolvimento-mvp-startups/ | FALHA | LCP 2879 ms, CLS 0.024 |
| /servicos/landing-page-conversao/ | passa | LCP 1829 ms, CLS 0.000 |
