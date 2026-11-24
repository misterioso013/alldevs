# AllDevs

Site autoral da AllDevs, criado para vender freelas de desenvolvimento com uma experiencia visual forte, direta e artesanal.

A proposta desta versao e voltar ao essencial: HTML e CSS gerados por um script Python simples, com JavaScript so como melhoria. Nada de framework por obrigação. A pagina precisa carregar rapido, comunicar valor em poucos segundos e ainda ter personalidade.

## Objetivo

Transformar a AllDevs em uma vitrine comercial para:

- vender servicos de sites, landing pages, apps, bots, MVPs e automacoes;
- mostrar dominio tecnico sem parecer um curriculo;
- reforcar a identidade de construtor rapido, pratico e orientado a produto;
- conduzir o visitante para contato pelo WhatsApp.

## Stack

- HTML e CSS estáticos, publicados pelo GitHub Pages (sem build no servidor)
- JavaScript vanilla, só como melhoria: o site funciona sem JS
- Gerador em Python (só biblioteca padrão) em `fonte/`
- Bancada de medição em Node (Playwright, axe, Lighthouse) em `bancada/`

## Estrutura

```text
.
├── index.html, projetos/, servicos/   # saída do gerador
├── css/        # tokens.css e site.css (escritos à mão)
├── js/         # scripts da página e js/vendor/
├── assets/     # imagens, fontes e paleta.json
├── fonte/      # gerador: modelos, conteúdo, dados (estudio.json etc.), testes
├── bancada/    # medição: capturas, axe, Lighthouse e paleta
├── docs/       # spec, plano e texto do PR
└── _config.yml # tira docs, bancada, fonte e este README do site publicado
```

As páginas HTML da raiz e das pastas do site são geradas: não edite à mão, edite `fonte/` e rode o gerador.
Telefone, e-mail e demais dados do estúdio ficam em `fonte/dados/estudio.json`.

## Gerador, testes e prévia

```bash
python3 fonte/gerar.py                  # reescreve a saída na raiz do repo
python3 -m unittest discover -s fonte/testes -t fonte
python3 fonte/checar.py                 # regras do projeto sobre a saída (rc 0 = limpo)
python3 fonte/gerar.py --previa --saida <pasta-fora-do-repo>   # prévia com noindex
bin/publicar-previa [--ensaio]         # envia a prévia à VPS (alldevs.docaio.com.br); --ensaio não toca na rede
```

Depois de gerar, `git diff` precisa ficar limpo (a saída é determinística).

## Bancada

Mede a prévia local: capturas em 360, 430 e 1440 px, axe, funcionamento sem JS, rolagem horizontal, links, movimento reduzido, FPS da home
(≥ 50 com CPU 4×) e Lighthouse (LCP e CLS). Como instalar e rodar: `bancada/LEIA.md`.

## Páginas principais

`index.html`  
Home comercial com serviços, projetos e contato.

`projetos/`  
Cases, um por pasta.

`servicos/*/index.html`  
Uma página por oferta, pensada para busca e conversão.

## Identidade

A AllDevs agora tem uma cara mais madura: tecnologia, velocidade e produto. A narrativa saiu do "grupo de devs" e passou para uma marca pessoal/comercial com lastro real:

- comeco programando pelo celular;
- primeiros freelas ainda menor de idade;
- Caio Guerras como a grande mente importante no inicio;
- AllDevs como laboratorio de automacoes e IA;
- produto com Machine Learning que passou de 100 mil usuarios;
- uso cedo de LLMs em processos reais;
- mentoria para desenvolvedores;
- ForjaDev como escola 1-on-1.

## Filosofia

Este projeto nao tenta parecer grande. Ele tenta parecer vivo.

O foco e comunicar rapidamente: se existe uma ideia, um processo travado ou um produto que precisa sair do papel, a AllDevs constrói com velocidade, clareza e tecnologia suficiente para resolver o problema certo.

## Agradecimentos
<center>
<img src="assets/images/caio.jpeg" alt="Caio Guerras" width="200">

A [Caio Guerras](https://www.linkedin.com/in/ocaioguerras/), por ser esse grande homem que inspirou e guiou os primeiros passos da AllDevs. Sem ele, nada disso existiria. Ele é a razão de tudo isso ter começado, e a AllDevs é uma extensão do legado que ele construiu. Obrigado, Caio, por tudo que você fez e continua fazendo pela comunidade de desenvolvedores. Você é uma lenda viva, e a AllDevs tem muito orgulho de ter sido parte da sua história.
</center>