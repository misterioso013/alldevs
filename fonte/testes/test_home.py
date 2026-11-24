"""Home completa (Task 6): ordem das seções, faixa de prova, cartões de projeto, passos, tecnologias, FAQ e contato."""
import dataclasses
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as D
from alldevs import paginas
from testes.test_conteudo import Base, ler
from testes.test_paginas import REPO, TITULOS, rodar

ORDEM = ["hero", "faixa", "ideia", "projetos", "servicos", "como-trabalhamos", "tecnologias", "quem-somos",
         "depoimentos", "faq", "contato"]
SERVICO_ANOS = "fonte/conteudo/servicos/criacao-de-sites-institucionais.html"
D_SERVICO_ANOS = SERVICO_ANOS
PROIBIDAS = ("servidor", "nuvem", "acervo", "Plex", "Jellyfin", "Emby", "CGSERVER", "torrent", "tracker")


def copia(testcase, editar=None):
    """Copia fonte/ e assets/ para um diretório temporário, aplica editar(raiz) e gera. Devolve (raiz, rc, erro)."""
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    raiz = Path(tmp.name) / "raiz"
    shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__", "testes"))
    shutil.copytree(REPO / "assets", raiz / "assets")
    if editar:
        editar(raiz)
    rc, _, err = rodar("--raiz", str(raiz))
    return raiz, rc, err


def secoes(txt):
    return re.findall(r'<section id="([a-z-]+)"', txt)


def secao(txt, id_):
    ini = txt.index(f'<section id="{id_}"')
    return txt[ini:txt.index("</section>", ini)]


class TestHome(Base):
    def setUp(self):
        self.home = ler(self.saida / "index.html")

    def test_ordem_das_secoes(self):
        # sem depoimentos autorizados (a lista é []), a seção não existe
        self.assertEqual(self.dados.depoimentos, ())
        self.assertEqual(secoes(self.home), [s for s in ORDEM if s != "depoimentos"])
        self.assertNotIn('id="depoimentos"', self.home)

    def test_depoimentos_aparece_com_um_autorizado(self):
        def editar(raiz):
            (raiz / "fonte/dados/depoimentos.json").write_text(json.dumps([
                {"nome": "Ana Teste", "papel": "Cliente", "texto": "Entregaram no prazo.", "autorizado": True}]),
                encoding="utf-8")
        raiz, rc, err = copia(self, editar)
        self.assertEqual(rc, 0, err)
        txt = ler(raiz / "index.html")
        self.assertEqual(secoes(txt), ORDEM)
        dep = secao(txt, "depoimentos")
        self.assertIn("Entregaram no prazo.", dep)
        self.assertIn("Ana Teste", dep)

    def test_faixa_prova_numeros_dos_dados(self):
        faixa = secao(self.home, "faixa")
        nums = [int(n) for n in re.findall(r'<strong class="faixa-num">(\d+)', faixa)]
        anos = int(re.search(r"mais de (\d+) anos", ler(REPO / SERVICO_ANOS)).group(1))
        no_ar = [p for p in self.visiveis
                 if not p.rascunho and p.situacao == "no ar" and (p.link or p.loja)]
        self.assertEqual(nums, [anos, len(no_ar), len(self.dados.tecnologias)])
        self.assertEqual(nums, [8, 6, 23])

    def test_faixa_prova_falha_alto_sem_o_texto_de_origem(self):
        def editar(raiz):
            arq = raiz / SERVICO_ANOS
            arq.write_text(arq.read_text(encoding="utf-8").replace("mais de 8 anos", "muitos anos"), encoding="utf-8")
        _, rc, err = copia(self, editar)
        self.assertEqual(rc, 1)
        self.assertIn("mais de", err)

    def test_faixa_prova_conta_so_projeto_no_ar_com_link(self):
        def editar(raiz):
            arq = raiz / "fonte/dados/projetos.json"
            ps = json.loads(arq.read_text(encoding="utf-8"))
            ps[0]["situacao"] = "encerrado"
            arq.write_text(json.dumps(ps), encoding="utf-8")
        raiz, rc, err = copia(self, editar)
        self.assertEqual(rc, 0, err)
        nums = re.findall(r'<strong class="faixa-num">(\d+)', ler(raiz / "index.html"))
        self.assertEqual(nums[1], "5")

    def test_destaques_sao_os_visiveis_com_destaque(self):
        # migrado de test_conteudo: o cartão de destaque agora é o .projeto-cartao
        esperados = [p.slug for p in self.visiveis if p.destaque]
        achados = re.findall(r'class="projeto-cartao"[^>]*data-slug="([^"]+)"', self.home)
        self.assertEqual(achados, esperados)

    def test_cartoes_de_servico_da_home_sem_selo_nem_degrade(self):
        # migrado de test_conteudo: o cartão ganhou data-revela, e segue sem selo nem nome de sócio
        cartoes = re.findall(r'<article class="cartao-servico[^"]*"[^>]*>.*?</article>', self.home, re.S)
        self.assertEqual(len(cartoes), len(self.dados.servicos))
        for c in cartoes:
            self.assertTrue(c.startswith('<article class="cartao-servico"'), c)
            self.assertNotIn("selo", c)
            self.assertNotIn("Caio", c)
            self.assertNotIn("Rosiel", c)

    def test_tres_produtos_reais_com_link_antes_do_fim(self):
        proj = secao(self.home, "projetos")
        cartoes = re.findall(r'<article class="projeto-cartao".*?</article>', proj, re.S)
        self.assertEqual(len(cartoes), len([p for p in self.visiveis if p.destaque]))
        externos = 0
        for c in cartoes:
            hrefs = re.findall(r'<a [^>]*href="(https://[^"]+)"', c)
            if hrefs:
                externos += 1
                self.assertRegex(c, r'target="_blank" rel="noopener"')
        self.assertGreaterEqual(externos, 3)

    def test_cartao_com_por_tras_aria_hidden(self):
        proj = secao(self.home, "projetos")
        for p in (x for x in self.visiveis if x.destaque):
            m = re.search(rf'<article class="projeto-cartao"[^>]*data-slug="{p.slug}".*?</article>', proj, re.S)
            self.assertIsNotNone(m, p.slug)
            c = m.group(0)
            camada = re.findall(r'<div class="cartao-por-tras"[^>]*>', c)
            if p.por_tras:
                self.assertEqual(camada, ['<div class="cartao-por-tras" aria-hidden="true">'], p.slug)
                self.assertNotIn("data-revela-cartao", c.split(">", 1)[0])  # a revelação mora na figura, não no cartão
                fig = re.search(r"<figure [^>]*>.*?</figure>", c, re.S).group(0)
                self.assertRegex(fig.split(">", 1)[0], r'\sdata-revela-cartao[\s>]')
                self.assertIn('data-cursor="ver por trás"', fig.split(">", 1)[0])
                self.assertIn('class="cartao-por-tras"', fig)  # a camada fica dentro da figura: nunca cobre h3 nem link
                self.assertNotRegex(fig[fig.index("cartao-por-tras"):], r"<a |<button")  # nada focável na camada
            else:
                self.assertEqual(camada, [], p.slug)
                self.assertNotIn("data-revela-cartao", c)

    def test_cartao_usa_a_frente_webp_lazy_sem_prioridade(self):
        proj = secao(self.home, "projetos")
        for img in re.findall(r"<img [^>]+>", proj):
            self.assertRegex(img, r'src="/assets/[^"]+\.webp"')
            self.assertRegex(img, r'width="\d+" height="\d+"')
            self.assertIn('loading="lazy"', img)
            self.assertIn('decoding="async"', img)
            self.assertNotIn("fetchpriority", img)
        self.assertEqual(len(re.findall(r'<img [^>]*fetchpriority="high"', self.home)), 1)  # só a frente do hero (o preload do head é a dica da mesma imagem)

    def test_imagens_do_cartao_dentro_do_teto_de_largura(self):
        proj = secao(self.home, "projetos")
        n = 0
        for img in re.findall(r"<img [^>]+>", proj):
            w, h = (int(x) for x in re.search(r'width="(\d+)" height="(\d+)"', img).groups())
            self.assertLessEqual(w, 540 if h > w else 960, img)
            n += 1
        self.assertGreaterEqual(n, 5)

    def test_img_da_camada_leva_largura_e_altura(self):
        # ramo sem código: a camada é uma imagem e leva width/height (sem salto de layout)
        proj = dataclasses.replace(next(p for p in self.dados.projetos if p.slug == "heisuca"),
                                   por_tras={"frente": "assets/frente/heisuca.webp", "arquivo": "assets/frente/heisuca.webp",
                                             "origem": "[x]"})
        camada = paginas._camada_por_tras(proj, REPO)
        self.assertRegex(camada, r'<img src="/assets/frente/heisuca.webp" width="\d+" height="\d+"')

    def test_cartao_sem_vocabulario_de_servidor_e_sem_cor_de_socio(self):
        proj = secao(self.home, "projetos")
        for slug in ("heisuca", "cgflix-lite"):
            c = re.search(rf'<article class="projeto-cartao"[^>]*data-slug="{slug}".*?</article>', proj, re.S).group(0)
            for palavra in PROIBIDAS:
                self.assertNotIn(palavra.lower(), c.lower(), f"{slug}: {palavra}")
        faixa = secao(self.home, "faixa")
        for palavra in PROIBIDAS:
            self.assertNotIn(palavra.lower(), faixa.lower())
        self.assertNotRegex(proj, r"(?i)\b(caio|rosiel)\b")  # projeto é do estúdio, nunca de um sócio

    def test_css_nao_liga_cor_a_socio(self):
        css = ler(REPO / "css/site.css")
        self.assertNotRegex(css, r"(?i)\b(caio|rosiel)\b")
        # a cor do por_tras, se exposta, é a mesma regra para todos os cartões: nada de seletor por slug
        self.assertNotRegex(css, r"projeto-cartao\[data-slug")
        proj = secao(self.home, "projetos")
        self.assertNotIn("data-cor", proj)

    def test_como_trabalhamos_4_passos(self):
        sec = secao(self.home, "como-trabalhamos")
        passos = re.findall(r'<li class="passo"', sec)
        self.assertEqual(len(passos), 4)
        arq = json.loads(ler(REPO / "fonte/conteudo/como-trabalhamos.json"))
        self.assertEqual(len(arq["passos"]), 4)
        for p in arq["passos"]:
            self.assertIn(p["titulo"], sec)
        self.assertEqual(re.findall(r'<span class="passo-num">(\d\d)</span>', sec), ["01", "02", "03", "04"])

    def test_passos_servem_a_todo_servico(self):
        arq = json.loads(ler(REPO / "fonte/conteudo/como-trabalhamos.json"))
        for p in arq["passos"]:
            for proibida in ("HTML", "PageSpeed", "layout das páginas", "semântico", "SEO", "domínio"):
                self.assertNotIn(proibida, p["texto"], p["titulo"])
            if "7 dias" in p["texto"]:
                self.assertIn("após a aprovação do briefing", p["texto"])
            self.assertTrue(p["fonte"].strip())

    def test_faq_no_maximo_uma_pergunta_por_servico(self):
        slugs = [s for s, _ in paginas.FAQ_HOME]
        self.assertEqual(len(slugs), len(set(slugs)), slugs)
        self.assertNotIn("criacao-de-sites-institucionais", slugs)
        sec = secao(self.home, "faq")
        for palavra in ("site institucional", "domínio", "HTML"):
            self.assertNotIn(palavra, sec)

    def test_como_trabalhamos_invalido_e_erro_de_dados(self):
        def editar(raiz):
            (raiz / "fonte/conteudo/como-trabalhamos.json").write_text(
                json.dumps({"passos": [{"titulo": "Só um", "texto": "x", "fonte": "y"}]}), encoding="utf-8")
        _, rc, err = copia(self, editar)
        self.assertEqual(rc, 1)
        self.assertIn("como-trabalhamos.json", err)

    def test_tecnologias_agrupadas_por_grupo_em_mono(self):
        sec = secao(self.home, "tecnologias")
        for g in D.GRUPOS_TECNOLOGIA:
            if any(t.grupo == g for t in self.dados.tecnologias):
                self.assertRegex(sec, rf'data-grupo="{g}"')
        for t in self.dados.tecnologias:
            self.assertIn(f">{t.nome}</li>", sec.replace("&amp;", "&"))
        self.assertEqual(len(re.findall(r'<li class="tecnologia"', sec)), len(self.dados.tecnologias))

    def test_grupos_do_rotulo_sao_os_grupos_validos(self):
        self.assertEqual({c for c, _ in paginas.GRUPOS_ROTULO}, set(D.GRUPOS_TECNOLOGIA))

    def test_sem_numero_solto(self):
        self.assertIn("%5Bsite%C2%B7home%5D", self.home)
        self.assertNotIn("contato@all.dev.br", self.home)
        links = re.findall(r'href="((?:https://wa\.me/|mailto:)[^"]*)"', self.home)
        self.assertGreaterEqual(len(links), 2)
        for h in links:
            self.assertIn("%5Bsite%C2%B7home%5D", h, h)   # toda origem de contato vem marcada
        sem_href = re.sub(r'href="[^"]*"', "", re.sub(r"<(script|style)\b.*?</\1>", "", self.home, flags=re.S))
        texto = re.sub(r"\d{4}-\d{2}-\d{2}", "data", re.sub(r"<[^>]+>", " ", sem_href))
        self.assertNotRegex(texto, r"(?<![\d.,])\+?\d[\d ()-]{8,}\d(?![\d])", "telefone solto no texto")

    def test_seta_do_faq_escondida_dos_leitores(self):
        for svg in re.findall(r"<svg[^>]*>", secao(self.home, "faq")):
            self.assertIn('aria-hidden="true"', svg)
            self.assertIn('focusable="false"', svg)

    def test_faq_desativado_sem_js(self):
        sec = secao(self.home, "faq")
        botoes = re.findall(r'<button [^>]*class="faq-question"[^>]*>', sec)
        self.assertEqual(len(botoes), 4)
        for b in botoes:
            self.assertRegex(b, r"\sdisabled[\s>]")
            self.assertIn('aria-expanded="true"', b)
        # as respostas são as das páginas de serviço, palavra por palavra
        fontes = "".join(ler(REPO / "fonte/conteudo/servicos" / f"{s}.html") for s in TITULOS)
        for resp in re.findall(r'<div class="faq-answer"><p>(.*?)</p></div>', sec, re.S):
            self.assertIn(resp, fontes)

    def test_quem_somos_sem_projeto_por_pessoa(self):
        sec = secao(self.home, "quem-somos")
        self.assertEqual(len(re.findall(r'<article class="cartao-pessoa"', sec)), 2)
        self.assertNotIn("data-sortear", sec)   # ordem fixa (crítica r2)
        for p in self.dados.projetos:
            self.assertNotIn(p.nome, sec)
            self.assertNotIn(f"/projetos/{p.slug}/", sec)

    def test_contato_com_um_unico_id(self):
        self.assertEqual(self.home.count('id="contato"'), 1)
        self.assertEqual(len(re.findall(r'\sid="([^"]+)"', self.home)),
                         len(set(re.findall(r'\sid="([^"]+)"', self.home))))  # nenhum id repetido
        self.assertIn("btn-cheio", secao(self.home, "contato"))

    def test_titulos_das_secoes_novas_com_titulo_revela(self):
        for s in ("projetos", "servicos", "como-trabalhamos", "tecnologias", "quem-somos", "faq", "contato"):
            self.assertRegex(secao(self.home, s), r'<h2 class="titulo-revela">', s)


class TestRobustez(Base):
    """Rodada 1 da Task 6: o gerador falha alto, com o caminho, e não deixa marcação nem escape se perder."""

    def _raiz(self, editar=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name) / "raiz"
        shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__", "testes"))
        shutil.copytree(REPO / "assets", raiz / "assets")
        if editar:
            editar(raiz)
        return raiz

    def test_faq_sem_o_html_do_servico_vira_erro_de_dados(self):
        raiz = self._raiz(lambda r: (r / "fonte/conteudo/servicos/landing-page-conversao.html").unlink())
        with self.assertRaises(D.ErroDeDados) as cm:
            paginas._faq_home(raiz)
        self.assertIn("landing-page-conversao.html", str(cm.exception))

    def test_faixa_sem_o_html_do_servico_vira_erro_de_dados(self):
        raiz = self._raiz(lambda r: (r / D_SERVICO_ANOS).unlink())
        with self.assertRaises(D.ErroDeDados) as cm:
            paginas._faixa_prova(self.dados, raiz)
        self.assertIn("criacao-de-sites-institucionais.html", str(cm.exception))

    def test_gerar_sem_o_html_do_servico_sai_com_rc_1_sem_traceback(self):
        _, rc, err = copia(self, lambda r: (r / "fonte/conteudo/servicos/landing-page-conversao.html").unlink())
        self.assertEqual(rc, 1)
        self.assertNotIn("Traceback", err)

    def test_sem_como_trabalhamos_json_e_erro_de_dados(self):
        _, rc, err = copia(self, lambda r: (r / "fonte/conteudo/como-trabalhamos.json").unlink())
        self.assertEqual(rc, 1)
        self.assertIn("como-trabalhamos.json", err)
        self.assertNotIn("Traceback", err)

    def test_bloco_de_contato_recebe_o_id_por_parametro(self):
        com = str(paginas._bloco_contato(self.dados.estudio, "home"))
        sem = str(paginas._bloco_contato(self.dados.estudio, "home", com_id=False))
        self.assertEqual(com.count('id="contato"'), 1)
        self.assertEqual(sem.count('id="contato"'), 0)
        self.assertIn('class="cta-buttons"', sem)
        home = ler(self.saida / "index.html")
        self.assertEqual(home.count('id="contato"'), 1)

    def _com_resposta(self, resposta):
        def editar(r):
            arq = r / "fonte/conteudo/servicos/landing-page-conversao.html"
            txt = arq.read_text(encoding="utf-8")
            velha = "O projeto inclui até 2 rodadas de revisão"
            self.assertIn(velha, txt)
            arq.write_text(txt.replace(velha, resposta + " O projeto inclui até 2 rodadas de revisão", 1), encoding="utf-8")
        return copia(self, editar)

    def test_faq_aceita_marcacao_permitida_sem_escape_duplo(self):
        raiz, rc, err = self._com_resposta('<strong>Sim</strong>, veja <a href="/x/">aqui</a> e <em>isso</em> e <code>x</code>.')
        self.assertEqual(rc, 0, err)
        sec = secao(ler(raiz / "index.html"), "faq")
        self.assertIn('<strong>Sim</strong>, veja <a href="/x/">aqui</a>', sec)
        self.assertNotIn("&lt;strong", sec)

    def test_faq_tag_fora_da_lista_diz_isso(self):
        _, rc, err = self._com_resposta('<img src="x.webp"> ')
        self.assertEqual(rc, 1)
        self.assertIn("tag", err)
        self.assertIn("img", err)
        self.assertNotIn("sumiu", err)

    def test_escape_do_hash_igual_no_hero_e_no_cartao(self):
        ciclo0 = self.dados.estudio.ciclo[0]
        proj = next(p for p in self.dados.projetos if p.slug == ciclo0)
        rel = proj.por_tras["arquivo"]

        def editar(r):
            arq = r / rel
            arq.write_text("// it's #fff e \"x\" & <b>\n" + arq.read_text(encoding="utf-8"), encoding="utf-8")
        raiz = self._raiz(editar)
        dados = D.carregar(raiz)
        proj = next(p for p in dados.projetos if p.slug == ciclo0)
        camada = paginas._camada_por_tras(proj, raiz)
        hero = str(paginas._hero(dados, raiz))
        for nome, html in (("cartão", camada), ("hero", hero)):
            self.assertIn("it&#x27;s &#35;fff", html, nome)
            self.assertNotIn("&amp;#x27;", html, nome)
            self.assertNotIn("&amp;#35;", html, nome)
            self.assertNotIn("#fff", html, nome)
            self.assertIn("&lt;b&gt;", html, nome)



class TestCartaoProjeto(unittest.TestCase):
    def test_cartao_projeto_devolve_seguro_e_escapa(self):
        dados = D.carregar(REPO)
        proj = dataclasses.replace(next(p for p in dados.projetos if p.slug == "prosup"), nome="A<b>&", resumo="x<i>")
        html = paginas._cartao_projeto(proj, REPO)
        self.assertIsInstance(html, paginas.Seguro)
        self.assertNotIn("<b>", html)
        self.assertIn("A&lt;b&gt;&amp;", html)
        self.assertIn('<h3><a href="/projetos/prosup/">', html)
        self.assertIn("<h2>", str(paginas._cartao_projeto(proj, REPO, nivel=2)))


if __name__ == "__main__":
    unittest.main()
