from abc import ABC, abstractmethod
from typing import List

# ==========================================
# HERANÇA E POLIMORFISMO
# ==========================================
class DificuldadeJogo(ABC):
    @abstractmethod
    def obter_max_tentativas(self) -> int:
        pass

    @abstractmethod
    def obter_nome(self) -> str:
        pass

class ModoFacil(DificuldadeJogo):
    def obter_max_tentativas(self) -> int:
        return 7
    def obter_nome(self) -> str:
        return "Fácil"

class ModoMedio(DificuldadeJogo):
    def obter_max_tentativas(self) -> int:
        return 6
    def obter_nome(self) -> str:
        return "Médio"

class ModoDificil(DificuldadeJogo):
    def obter_max_tentativas(self) -> int:
        return 5
    def obter_nome(self) -> str:
        return "Difícil"

# ==========================================
# ENCAPSULAMENTO, COMPOSIÇÃO E ASSOCIAÇÃO
# ==========================================
class Celula:
    def __init__(self, letra: str = ""):
        self.__letra = letra.upper()
        self.__status = "VAZIA"  # VAZIA, CORRETA, DESLOCADA, INCORRETA

    @property
    def letra(self) -> str:
        return self.__letra

    @letra.setter
    def letra(self, valor: str):
        self.__letra = valor.upper()[:1]

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, valor: str):
        if valor in ["VAZIA", "CORRETA", "DESLOCADA", "INCORRETA"]:
            self.__status = valor

class Linha:
    def __init__(self, tamanho: int = 5):
        # COMPOSIÇÃO: Linha cria e possui suas próprias Células
        self.__celulas = [Celula() for _ in range(tamanho)]

    @property
    def celulas(self) -> List[Celula]:
        return self.__celulas

    def preencher_palavra(self, palavra: str):
        for i, letra in enumerate(palavra[:len(self.__celulas)]):
            self.__celulas[i].letra = letra

class Tabuleiro:
    def __init__(self, dificuldade: DificuldadeJogo, palavra_secreta: str):
        self.__dificuldade = dificuldade  # ASSOCIAÇÃO
        self.__palavra_secreta = palavra_secreta.upper()
        self.__rodada_atual = 0
        
        # COMPOSIÇÃO: O Tabuleiro controla a instanciação das Linhas
        max_tentativas = self.__dificuldade.obter_max_tentativas()
        self.__linhas = [Linha(len(palavra_secreta)) for _ in range(max_tentativas)]

    @property
    def rodada_atual(self) -> int:
        return self.__rodada_atual

    @rodada_atual.setter
    def rodada_atual(self, valor: int):
        if valor >= 0:
            self.__rodada_atual = valor

    @property
    def linhas(self) -> List[Linha]:
        return self.__linhas

    @property
    def palavra_secreta(self) -> str:
        return self.__palavra_secreta