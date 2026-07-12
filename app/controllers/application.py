import random
import os
from bottle import template
from ..models.models import Tabuleiro, ModoFacil, ModoMedio, ModoDificil

class Application():

    def __init__(self):
        self.pages = {
            'index': self.index, 
            'pagina': self.pagina,
            'rankings': self.rankings 
        }
        self.__tabuleiro = None
        self.__jogador_atual = None

    def render(self, page):
        content = self.pages.get(page, self.helper)
        return content()

    def helper(self):
        return template('app/views/html/helper')

    def index(self): 
        return template('app/views/html/index')

    def pagina(self):
        return template('app/views/html/pagina')

    def rankings(self): 
        return template('app/views/html/rankings')

    def novo_jogo(self, modo: str, username: str = "Convidado") -> dict:
        try:
            from ..models.models import Jogador
            self.__jogador_atual = Jogador(username)
        except ImportError:
            self.__jogador_atual = None

        if modo == "facil":
            dificuldade = ModoFacil()
        elif modo == "dificil":
            dificuldade = ModoDificil()
        else:
            dificuldade = ModoMedio()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_palavras = os.path.join(base_dir, "palavras.txt")

        with open(caminho_palavras, "r", encoding="utf-8") as arquivo:
            palavras = arquivo.read().splitlines()

        palavra_secreta = random.choice(palavras)
        self.__tabuleiro = Tabuleiro(dificuldade, palavra_secreta)
        
        resposta = {
            "status": "Jogo iniciado",
            "tentativas_maximas": dificuldade.obter_max_tentativas(),
            "tamanho_palavra": len(palavra_secreta)
        }

        if self.__jogador_atual:
            resposta["jogador_stats"] = {
                "vitorias_totais": self.__jogador_atual.vitorias_totais,
                "vitorias_seguidas": self.__jogador_atual.vitorias_seguidas
            }
        return resposta

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

        letras_restantes = list(secreta)
        
        for i, celula in enumerate(linha_atual.celulas):
            if celula.letra == secreta[i]:
                celula.status = "CORRETA"
                letras_restantes[i] = None

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

        if ganhou and self.__jogador_atual:
            self.__jogador_atual.registrar_vitoria(self.__tabuleiro.dificuldade.obter_nome())
        elif perdeu and self.__jogador_atual:
            self.__jogador_atual.registrar_derrota()

        resposta_dict = {
            "letras": [{"letra": c.letra, "status": c.status} for c in linha_atual.celulas],
            "ganhou": ganhou,
            "perdeu": perdeu,
            "rodada_atual": self.__tabuleiro.rodada_atual,
            "fim_de_jogo": ganhou or perdeu,
            "resposta": secreta if perdeu else None
        }

        if self.__jogador_atual:
            resposta_dict["jogador_stats"] = {
                "vitorias_totais": self.__jogador_atual.vitorias_totais,
                "vitorias_seguidas": self.__jogador_atual.vitorias_seguidas
            }
        return resposta_dict

    def obter_rankings_data(self) -> dict:
        try:
            from ..models.models import Jogador
            return {
                "top_vitorias": Jogador.obter_top_vitorias(),
                "top_sequencias": Jogador.obter_top_sequencias()
            }
        except Exception:
            return {"top_vitorias": [], "top_sequencias": []}