import random
from bottle import template
from ..models.models import Tabuleiro, ModoFacil, ModoMedio, ModoDificil

class Application():

    def __init__(self):
        self.pages = {
            'pagina': self.pagina
        }
        self.__tabuleiro = None

    def render(self, page):
        content = self.pages.get(page, self.helper)
        return content()

    def helper(self):
        return template('app/views/html/helper')

    def pagina(self):
        return template('app/views/html/pagina')

    # ==========================================
    # REGRAS DE NEGÓCIO E FLUXO DO JOGO TERMO
    # ==========================================
    def novo_jogo(self, modo: str) -> dict:
        if modo == "facil":
            dificuldade = ModoFacil()
        elif modo == "dificil":
            dificuldade = ModoDificil()
        else:
            dificuldade = ModoMedio()

        with open("app/controllers/palavras.txt", "r", encoding="utf-8") as arquivo:
            palavras = arquivo.read().splitlines()

        palavra_secreta = random.choice(palavras)

        self.__tabuleiro = Tabuleiro(dificuldade, palavra_secreta)
        
        return {
            "status": "Jogo iniciado",
            "tentativas_maximas": dificuldade.obter_max_tentativas(),
            "tamanho_palavra": len(palavra_secreta)
        }

    def processar_tentativa(self, palpite: str) -> dict:
        if not self.__tabuleiro:
            return {"erro": "Nenhum jogo em andamento."}

        rodada = self.__tabuleiro.rodada_atual
        if rodada >= len(self.__tabuleiro.linhas):
            return {"erro": "Limite de tentativas alcançado."}

        palpite = palpite.upper()
        secreta = self.__tabuleiro.palavra_secreta

        if len(palpite) != len(secreta):
            return {"erro": f"A palavra deve ter {len(secreta)} letras."}

        linha_atual = self.__tabuleiro.linhas[rodada]
        linha_atual.preencher_palavra(palpite)

        # Lógica de validação das cores (Verde, Amarelo, Cinza, Vermelho)
        letras_restantes = list(secreta)
        
        # 1 - Posições exatas (CORRETA)
        for i, celula in enumerate(linha_atual.celulas):
            if celula.letra == secreta[i]:
                celula.status = "CORRETA"
                letras_restantes[i] = None

        # 2 - Passada: Posições deslocadas (DESLOCADA) ou erradas (INCORRETA)
        for i, celula in enumerate(linha_atual.celulas):
            if celula.status != "CORRETA":
                if celula.letra in letras_restantes and celula.letra is not None:
                    celula.status = "DESLOCADA"
                    letras_restantes[letras_restantes.index(celula.letra)] = None
                else:
                    celula.status = "INCORRETA"

        self.__tabuleiro.rodada_atual += 1

        ganhou = palpite == secreta
        perdeu = not ganhou and self.__tabuleiro.rodada_atual >= len(self.__tabuleiro.linhas)

        return {
            "letras": [{"letra": c.letra, "status": c.status} for c in linha_atual.celulas],
            "ganhou": ganhou,
            "perdeu": perdeu,
            "rodada_atual": self.__tabuleiro.rodada_atual,
            "fim_de_jogo": ganhou or perdeu,
            "resposta": secreta if perdeu else None
        }