# Relatório da bancada

Base: http://127.0.0.1:8765 — 15 páginas — gerado em 2026-11-22T15:00:55.046Z

## Resumo

| Meta | Resultado | Falhas |
|---|---|---|
| Capturas em 430 e 1440 px | PASSA | 0/15 páginas |
| axe: zero problemas serious/critical | FALHA | 13/15 páginas |
| Sem JS: título, contato e (em /projetos/) todos os cards | FALHA | 3/15 páginas |
| Sem rolagem horizontal em 430 px | PASSA | 0/15 páginas |
| Links internos respondem 200, sem redirecionamento | PASSA | 0/15 páginas |
| reducedMotion: nenhum transform após 1 s | FALHA | 4/15 páginas |
| Lighthouse móvel: LCP < 2500 ms e CLS < 0,05 | FALHA | 3/15 páginas |

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
| / | FALHA | color-contrast (serious, 27) |
| /caio/ | FALHA | color-contrast (serious, 15) |
| /historia.html | FALHA | color-contrast (serious, 28) |
| /projetos/ | FALHA | color-contrast (serious, 18) |
| /projetos/fakly/ | FALHA | color-contrast (serious, 14) |
| /projetos/heisuca/ | FALHA | color-contrast (serious, 14) |
| /projetos/prosup/ | FALHA | color-contrast (serious, 14) |
| /projetos/sendany/ | FALHA | color-contrast (serious, 14) |
| /rosiel/ | FALHA | color-contrast (serious, 18) |
| /servicos/aplicativo-mobile-react-native/ | FALHA | color-contrast (serious, 4) |
| /servicos/automacoes-integracoes-api/ | FALHA | color-contrast (serious, 4) |
| /servicos/bots-whatsapp-automacao/ | FALHA | color-contrast (serious, 4) |
| /servicos/criacao-de-sites-institucionais/ | FALHA | color-contrast (serious, 4) |
| /servicos/desenvolvimento-mvp-startups/ | passa | 0 graves (2 leves) |
| /servicos/landing-page-conversao/ | passa | 0 graves (2 leves) |

## Sem JS: título, contato e (em /projetos/) todos os cards

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | h1 "Fazemos software que vive.", contato 3 |
| /caio/ | passa | h1 "Caio Guerras", contato 3 |
| /historia.html | passa | h1 "Uma históriafora do roteiro", contato 3 |
| /projetos/ | passa | h1 "Projetos", contato 3, cards 4/4 |
| /projetos/fakly/ | passa | h1 "Fakly", contato 3 |
| /projetos/heisuca/ | passa | h1 "Heisuca", contato 3 |
| /projetos/prosup/ | passa | h1 "ProsUp", contato 3 |
| /projetos/sendany/ | passa | h1 "SendAny", contato 3 |
| /rosiel/ | passa | h1 "Rosiel Victor", contato 3 |
| /servicos/aplicativo-mobile-react-native/ | passa | h1 "Desenvolvimento de Aplicativo Mobile iOS e Android com React Native", contato 3 |
| /servicos/automacoes-integracoes-api/ | passa | h1 "Automação de Processos e Integração de Sistemas via API e Webhook", contato 3 |
| /servicos/bots-whatsapp-automacao/ | passa | h1 "Bot para WhatsApp, Discord e Telegram — Automação de Atendimento 24h", contato 3 |
| /servicos/criacao-de-sites-institucionais/ | FALHA | sem contato |
| /servicos/desenvolvimento-mvp-startups/ | FALHA | sem contato |
| /servicos/landing-page-conversao/ | FALHA | sem contato |

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
| /projetos/fakly/ | passa | 13 ok |
| /projetos/heisuca/ | passa | 13 ok |
| /projetos/prosup/ | passa | 13 ok |
| /projetos/sendany/ | passa | 13 ok |
| /rosiel/ | passa | 17 ok |
| /servicos/aplicativo-mobile-react-native/ | passa | 19 ok |
| /servicos/automacoes-integracoes-api/ | passa | 18 ok |
| /servicos/bots-whatsapp-automacao/ | passa | 17 ok |
| /servicos/criacao-de-sites-institucionais/ | passa | 0 ok |
| /servicos/desenvolvimento-mvp-startups/ | passa | 0 ok |
| /servicos/landing-page-conversao/ | passa | 0 ok |

## reducedMotion: nenhum transform após 1 s

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | nenhum |
| /caio/ | passa | nenhum |
| /historia.html | FALHA | 12: div#hk.hist-kicker = matrix(1, 0, 0, 1, 0, 0); h1#ht.hist-title = matrix(1, 0, 0, 1, 0, 0.0018); p#hs.hist-sub = matrix(1, 0, 0, 1, 0, 0.7356); div.tl-content.reveal = matrix(1, 0, 0, 1, 0, 40); div.tl-content.reveal = matrix(1, 0, 0, 1, 0, 40) |
| /projetos/ | passa | nenhum |
| /projetos/fakly/ | passa | nenhum |
| /projetos/heisuca/ | passa | nenhum |
| /projetos/prosup/ | passa | nenhum |
| /projetos/sendany/ | passa | nenhum |
| /rosiel/ | passa | nenhum |
| /servicos/aplicativo-mobile-react-native/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/automacoes-integracoes-api/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/bots-whatsapp-automacao/ | FALHA | 5: div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16); div.faq-item = matrix(1, 0, 0, 1, 0, 16) |
| /servicos/criacao-de-sites-institucionais/ | passa | nenhum |
| /servicos/desenvolvimento-mvp-startups/ | passa | nenhum |
| /servicos/landing-page-conversao/ | passa | nenhum |

## Lighthouse móvel: LCP < 2500 ms e CLS < 0,05

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | LCP 1372 ms, CLS 0.038 |
| /caio/ | FALHA | LCP 2586 ms, CLS 0.007 |
| /historia.html | passa | LCP 1923 ms, CLS 0.015 |
| /projetos/ | passa | LCP 1372 ms, CLS 0.001 |
| /projetos/fakly/ | passa | LCP 1373 ms, CLS 0.001 |
| /projetos/heisuca/ | passa | LCP 1373 ms, CLS 0.000 |
| /projetos/prosup/ | passa | LCP 1372 ms, CLS 0.000 |
| /projetos/sendany/ | passa | LCP 1372 ms, CLS 0.001 |
| /rosiel/ | FALHA | LCP 3152 ms, CLS 0.007 |
| /servicos/aplicativo-mobile-react-native/ | passa | LCP 1526 ms, CLS 0.018 |
| /servicos/automacoes-integracoes-api/ | FALHA | LCP 2732 ms, CLS 0.024 |
| /servicos/bots-whatsapp-automacao/ | passa | LCP 1834 ms, CLS 0.048 |
| /servicos/criacao-de-sites-institucionais/ | passa | LCP 603 ms, CLS 0.000 |
| /servicos/desenvolvimento-mvp-startups/ | passa | LCP 603 ms, CLS 0.000 |
| /servicos/landing-page-conversao/ | passa | LCP 603 ms, CLS 0.000 |
