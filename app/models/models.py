from abc import ABC, abstractmethod
from typing import List
import sqlite3

# --- BANCO DE DADOS E JOGADOR ---

def conectar_db():
    conn = sqlite3.connect('app/controllers/db/termo.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    conn = conectar_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            username TEXT PRIMARY KEY,
            vitorias_totais INTEGER DEFAULT 0,
            vitorias_seguidas INTEGER DEFAULT 0,
            vitorias_facil INTEGER DEFAULT 0,
            vitorias_medio INTEGER DEFAULT 0,
            vitorias_dificil INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

inicializar_db()

class Jogador:
    def __init__(self, username: str):
        self.username = username.upper()
        self.carregar_ou_criar()

    def carregar_ou_criar(self):
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jogadores WHERE username = ?", (self.username,))
        row = cursor.fetchone()
        
        if row is None:
            cursor.execute("INSERT INTO jogadores (username) VALUES (?)", (self.username,))
            conn.commit()
            self.vitorias_totais = 0
            self.vitorias_seguidas = 0
            self.vitorias_facil = 0
            self.vitorias_medio = 0
            self.vitorias_dificil = 0
        else:
            self.vitorias_totais = row['vitorias_totais']
            self.vitorias_seguidas = row['vitorias_seguidas']
            self.vitorias_facil = row['vitorias_facil']
            self.vitorias_medio = row['vitorias_medio']
            self.vitorias_dificil = row['vitorias_dificil']
        conn.close()

    def registrar_vitoria(self, nivel: str):
        self.vitorias_totais += 1
        self.vitorias_seguidas += 1
        
        if nivel == "facil": self.vitorias_facil += 1
        elif nivel == "medio": self.vitorias_medio += 1
        elif nivel == "dificil": self.vitorias_dificil += 1
        
        self._salvar()

    def registrar_derrota(self):
        self.vitorias_seguidas = 0
        self._salvar()

    def _salvar(self):
        conn = conectar_db()
        conn.execute('''
            UPDATE jogadores SET 
                vitorias_totais = ?, vitorias_seguidas = ?, 
                vitorias_facil = ?, vitorias_medio = ?, vitorias_dificil = ?
            WHERE username = ?
        ''', (self.vitorias_totais, self.vitorias_seguidas, self.vitorias_facil, 
              self.vitorias_medio, self.vitorias_dificil, self.username))
        conn.commit()
        conn.close()

    @staticmethod
    def obter_top_vitorias():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, vitorias_totais FROM jogadores ORDER BY vitorias_totais DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        return [{"username": r["username"], "vitorias_totais": r["vitorias_totais"]} for r in rows]

    @staticmethod
    def obter_top_sequencias():
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, vitorias_seguidas FROM jogadores ORDER BY vitorias_seguidas DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        return [{"username": r["username"], "vitorias_seguidas": r["vitorias_seguidas"]} for r in rows]

# --- MODELOS DO JOGO ---

class DificuldadeJogo(ABC):

    @abstractmethod
    def obter_max_tentativas(self) -> int: pass

    @abstractmethod
    def obter_nome(self) -> str: pass

class ModoFacil(DificuldadeJogo):
    def obter_max_tentativas(self) -> int: return 7
    def obter_nome(self) -> str: return "facil"

class ModoMedio(DificuldadeJogo):
    def obter_max_tentativas(self) -> int: return 6
    def obter_nome(self) -> str: return "medio"

class ModoDificil(DificuldadeJogo):
    def obter_max_tentativas(self) -> int: return 5
    def obter_nome(self) -> str: return "dificil"

class Celula:
    def __init__(self, letra: str = ""):
        self.__letra = letra.upper()
        self.__status = "VAZIA" 

    @property
    def letra(self) -> str: return self.__letra

    @letra.setter
    def letra(self, valor: str): self.__letra = valor.upper()[:1]

    @property
    def status(self) -> str: return self.__status

    @status.setter
    def status(self, valor: str):
        if valor in ["VAZIA", "CORRETA", "DESLOCADA", "INCORRETA"]:
            self.__status = valor

class Linha:
    def __init__(self, tamanho: int = 5):
        self.__celulas = [Celula() for _ in range(tamanho)]

    @property
    def celulas(self) -> List[Celula]: return self.__celulas

    def preencher_palavra(self, palavra: str):
        for i, letra in enumerate(palavra[:len(self.__celulas)]):
            self.__celulas[i].letra = letra

class Tabuleiro:
    def __init__(self, dificuldade: DificuldadeJogo, palavra_secreta: str):
        self.dificuldade = dificuldade 
        self.__palavra_secreta = palavra_secreta.upper()
        self.__rodada_atual = 0
        max_tentativas = self.dificuldade.obter_max_tentativas()
        self.__linhas = [Linha(len(palavra_secreta)) for _ in range(max_tentativas)]

    @property
    def rodada_atual(self) -> int: return self.__rodada_atual

    @rodada_atual.setter
    def rodada_atual(self, valor: int):
        if valor >= 0: self.__rodada_atual = valor

    @property
    def linhas(self) -> List[Linha]: return self.__linhas

    @property
    def palavra_secreta(self) -> str: return self.__palavra_secreta