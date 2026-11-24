# Relatório da bancada

Base: http://127.0.0.1:8765 — 16 páginas — gerado em 2026-11-24T17:45:37.608Z

## Resumo

| Meta | Resultado | Falhas |
|---|---|---|
| Capturas em 360, 430 e 1440 px | PASSA | 0/16 páginas |
| axe: zero problemas serious/critical (360, 430 e 1440 px) | PASSA | 0/16 páginas |
| Sem JS: título, contato e (em /projetos/) todos os cards | PASSA | 0/16 páginas |
| Sem rolagem horizontal em 360 e 430 px | PASSA | 0/16 páginas |
| Links internos respondem 200, sem redirecionamento | PASSA | 0/16 páginas |
| reducedMotion: nenhum transform após 1 s | PASSA | 0/16 páginas |
| Paleta: Ctrl K, seta, Enter navega e Esc devolve o foco (1440 px); toque na pílula (412 px); axe aberta; reduced-motion; sem rede | PASSA | 0/16 páginas |
| FPS ≥ 50 com CPU 4× mais lenta (só na /; 1440 px) | PASSA | 0/1 páginas |
| Lighthouse móvel: LCP < 2500 ms e CLS < 0,05 | FALHA | 1/16 páginas |

Código de saída: **1**

## Capturas em 360, 430 e 1440 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | home-360.png, home-430.png, home-1440.png |
| /projetos/ | passa | projetos-360.png, projetos-430.png, projetos-1440.png |
| /projetos/amott/ | passa | projetos_amott-360.png, projetos_amott-430.png, projetos_amott-1440.png |
| /projetos/cgflix-lite/ | passa | projetos_cgflix-lite-360.png, projetos_cgflix-lite-430.png, projetos_cgflix-lite-1440.png |
| /projetos/fakly/ | passa | projetos_fakly-360.png, projetos_fakly-430.png, projetos_fakly-1440.png |
| /projetos/forjadev/ | passa | projetos_forjadev-360.png, projetos_forjadev-430.png, projetos_forjadev-1440.png |
| /projetos/heisuca/ | passa | projetos_heisuca-360.png, projetos_heisuca-430.png, projetos_heisuca-1440.png |
| /projetos/huntar/ | passa | projetos_huntar-360.png, projetos_huntar-430.png, projetos_huntar-1440.png |
| /projetos/prosup/ | passa | projetos_prosup-360.png, projetos_prosup-430.png, projetos_prosup-1440.png |
| /projetos/sendany/ | passa | projetos_sendany-360.png, projetos_sendany-430.png, projetos_sendany-1440.png |
| /servicos/aplicativo-mobile-react-native/ | passa | servicos_aplicativo-mobile-react-native-360.png, servicos_aplicativo-mobile-react-native-430.png, servicos_aplicativo-mobile-react-native-1440.png |
| /servicos/automacoes-integracoes-api/ | passa | servicos_automacoes-integracoes-api-360.png, servicos_automacoes-integracoes-api-430.png, servicos_automacoes-integracoes-api-1440.png |
| /servicos/bots-whatsapp-automacao/ | passa | servicos_bots-whatsapp-automacao-360.png, servicos_bots-whatsapp-automacao-430.png, servicos_bots-whatsapp-automacao-1440.png |
| /servicos/criacao-de-sites-institucionais/ | passa | servicos_criacao-de-sites-institucionais-360.png, servicos_criacao-de-sites-institucionais-430.png, servicos_criacao-de-sites-institucionais-1440.png |
| /servicos/desenvolvimento-mvp-startups/ | passa | servicos_desenvolvimento-mvp-startups-360.png, servicos_desenvolvimento-mvp-startups-430.png, servicos_desenvolvimento-mvp-startups-1440.png |
| /servicos/landing-page-conversao/ | passa | servicos_landing-page-conversao-360.png, servicos_landing-page-conversao-430.png, servicos_landing-page-conversao-1440.png |

## axe: zero problemas serious/critical (360, 430 e 1440 px)

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/amott/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/cgflix-lite/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/fakly/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/forjadev/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/heisuca/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/huntar/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/prosup/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /projetos/sendany/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /servicos/aplicativo-mobile-react-native/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /servicos/automacoes-integracoes-api/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /servicos/bots-whatsapp-automacao/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /servicos/criacao-de-sites-institucionais/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /servicos/desenvolvimento-mvp-startups/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |
| /servicos/landing-page-conversao/ | passa | 0 graves em 360, 430 e 1440 px (1/1/0 leves) |

## Sem JS: título, contato e (em /projetos/) todos os cards

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | h1 "Fazemos software que vive.", contatos visíveis 3/4 |
| /projetos/ | passa | h1 "Projetos", contatos visíveis 3/4, cards visíveis 8/8 |
| /projetos/amott/ | passa | h1 "amott", contatos visíveis 3/4 |
| /projetos/cgflix-lite/ | passa | h1 "CGFLIX Lite", contatos visíveis 3/4 |
| /projetos/fakly/ | passa | h1 "Fakly", contatos visíveis 3/4 |
| /projetos/forjadev/ | passa | h1 "ForjaDev", contatos visíveis 3/4 |
| /projetos/heisuca/ | passa | h1 "Heisuca", contatos visíveis 3/4 |
| /projetos/huntar/ | passa | h1 "Huntar", contatos visíveis 3/4 |
| /projetos/prosup/ | passa | h1 "ProsUp", contatos visíveis 3/4 |
| /projetos/sendany/ | passa | h1 "SendAny", contatos visíveis 3/4 |
| /servicos/aplicativo-mobile-react-native/ | passa | h1 "Desenvolvimento de Aplicativo Mobile iOS e Android com React Native", contatos visíveis 4/5 |
| /servicos/automacoes-integracoes-api/ | passa | h1 "Automação de Processos e Integração de Sistemas via API e Webhook", contatos visíveis 4/5 |
| /servicos/bots-whatsapp-automacao/ | passa | h1 "Bot para WhatsApp, Discord e Telegram — Automação de Atendimento 24h", contatos visíveis 4/5 |
| /servicos/criacao-de-sites-institucionais/ | passa | h1 "Criação de Site Institucional Profissional para Empresas", contatos visíveis 4/5 |
| /servicos/desenvolvimento-mvp-startups/ | passa | h1 "Desenvolvimento de MVP Web para Startups — Do Zero ao Ar em Semanas", contatos visíveis 4/5 |
| /servicos/landing-page-conversao/ | passa | h1 "Landing Page de Alta Conversão com Integração WhatsApp", contatos visíveis 4/5 |

## Sem rolagem horizontal em 360 e 430 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/amott/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/cgflix-lite/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/fakly/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/forjadev/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/heisuca/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/huntar/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/prosup/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /projetos/sendany/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /servicos/aplicativo-mobile-react-native/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /servicos/automacoes-integracoes-api/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /servicos/bots-whatsapp-automacao/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /servicos/criacao-de-sites-institucionais/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /servicos/desenvolvimento-mvp-startups/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |
| /servicos/landing-page-conversao/ | passa | 360 px: scrollWidth 360 / clientWidth 360; 430 px: scrollWidth 430 / clientWidth 430 |

## Links internos respondem 200, sem redirecionamento

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 34 ok |
| /projetos/ | passa | 35 ok |
| /projetos/amott/ | passa | 21 ok |
| /projetos/cgflix-lite/ | passa | 24 ok |
| /projetos/fakly/ | passa | 22 ok |
| /projetos/forjadev/ | passa | 22 ok |
| /projetos/heisuca/ | passa | 23 ok |
| /projetos/huntar/ | passa | 22 ok |
| /projetos/prosup/ | passa | 23 ok |
| /projetos/sendany/ | passa | 22 ok |
| /servicos/aplicativo-mobile-react-native/ | passa | 30 ok |
| /servicos/automacoes-integracoes-api/ | passa | 22 ok |
| /servicos/bots-whatsapp-automacao/ | passa | 21 ok |
| /servicos/criacao-de-sites-institucionais/ | passa | 27 ok |
| /servicos/desenvolvimento-mvp-startups/ | passa | 30 ok |
| /servicos/landing-page-conversao/ | passa | 26 ok |

## reducedMotion: nenhum transform após 1 s

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | nenhum |
| /projetos/ | passa | nenhum |
| /projetos/amott/ | passa | nenhum |
| /projetos/cgflix-lite/ | passa | nenhum |
| /projetos/fakly/ | passa | nenhum |
| /projetos/forjadev/ | passa | nenhum |
| /projetos/heisuca/ | passa | nenhum |
| /projetos/huntar/ | passa | nenhum |
| /projetos/prosup/ | passa | nenhum |
| /projetos/sendany/ | passa | nenhum |
| /servicos/aplicativo-mobile-react-native/ | passa | nenhum |
| /servicos/automacoes-integracoes-api/ | passa | nenhum |
| /servicos/bots-whatsapp-automacao/ | passa | nenhum |
| /servicos/criacao-de-sites-institucionais/ | passa | nenhum |
| /servicos/desenvolvimento-mvp-startups/ | passa | nenhum |
| /servicos/landing-page-conversao/ | passa | nenhum |

## Paleta: Ctrl K, seta, Enter navega e Esc devolve o foco (1440 px); toque na pílula (412 px); axe aberta; reduced-motion; sem rede

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 662 ms (<= 1000), 2ª visita sem overlay |
| /projetos/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 966 ms (<= 1000), 2ª visita sem overlay |
| /projetos/amott/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 727 ms (<= 1000), 2ª visita sem overlay |
| /projetos/cgflix-lite/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 706 ms (<= 1000), 2ª visita sem overlay |
| /projetos/fakly/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 718 ms (<= 1000), 2ª visita sem overlay |
| /projetos/forjadev/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 693 ms (<= 1000), 2ª visita sem overlay |
| /projetos/heisuca/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 949 ms (<= 1000), 2ª visita sem overlay |
| /projetos/huntar/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 721 ms (<= 1000), 2ª visita sem overlay |
| /projetos/prosup/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 739 ms (<= 1000), 2ª visita sem overlay |
| /projetos/sendany/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 957 ms (<= 1000), 2ª visita sem overlay |
| /servicos/aplicativo-mobile-react-native/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 710 ms (<= 1000), 2ª visita sem overlay |
| /servicos/automacoes-integracoes-api/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 709 ms (<= 1000), 2ª visita sem overlay |
| /servicos/bots-whatsapp-automacao/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 978 ms (<= 1000), 2ª visita sem overlay |
| /servicos/criacao-de-sites-institucionais/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 711 ms (<= 1000), 2ª visita sem overlay |
| /servicos/desenvolvimento-mvp-startups/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 713 ms (<= 1000), 2ª visita sem overlay |
| /servicos/landing-page-conversao/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/cgflix-lite/, Esc devolve o foco, 18 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/cgflix-lite/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho); preloader: 1ª visita some em 970 ms (<= 1000), 2ª visita sem overlay |

## FPS ≥ 50 com CPU 4× mais lenta (só na /; 1440 px)

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 54.4 fps com CPU 4x |

## Lighthouse móvel: LCP < 2500 ms e CLS < 0,05

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | LCP 2028 ms, CLS 0.000 |
| /projetos/ | FALHA | LCP 3696 ms, CLS 0.000 |
| /projetos/amott/ | passa | LCP 1855 ms, CLS 0.000 |
| /projetos/cgflix-lite/ | passa | LCP 1847 ms, CLS 0.000 |
| /projetos/fakly/ | passa | LCP 1908 ms, CLS 0.000 |
| /projetos/forjadev/ | passa | LCP 1702 ms, CLS 0.000 |
| /projetos/heisuca/ | passa | LCP 1853 ms, CLS 0.000 |
| /projetos/huntar/ | passa | LCP 1850 ms, CLS 0.005 |
| /projetos/prosup/ | passa | LCP 1849 ms, CLS 0.000 |
| /projetos/sendany/ | passa | LCP 1205 ms, CLS 0.000 |
| /servicos/aplicativo-mobile-react-native/ | passa | LCP 1880 ms, CLS 0.000 |
| /servicos/automacoes-integracoes-api/ | passa | LCP 2030 ms, CLS 0.000 |
| /servicos/bots-whatsapp-automacao/ | passa | LCP 2028 ms, CLS 0.015 |
| /servicos/criacao-de-sites-institucionais/ | passa | LCP 1354 ms, CLS 0.001 |
| /servicos/desenvolvimento-mvp-startups/ | passa | LCP 2034 ms, CLS 0.001 |
| /servicos/landing-page-conversao/ | passa | LCP 1354 ms, CLS 0.001 |
