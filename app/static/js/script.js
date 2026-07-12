let rodadaAtual = 0;
let tamanhoPalavra = 5;
let palpiteAtual = "";
let jogoAtivo = true;

document.addEventListener("DOMContentLoaded", iniciarJogo);

async function iniciarJogo() {
    const username = sessionStorage.getItem('termo_username') || "Convidado";
    const modo = sessionStorage.getItem('termo_dificuldade') || "medio";

    document.getElementById('btn-jogar-novamente').style.display = "none";
    document.getElementById('btn-voltar').style.display = "none";
    document.getElementById('mensagem').innerText = "";
    
    jogoAtivo = true;

    const response = await fetch('/api/iniciar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modo: modo, username: username })
    });

    const dados = await response.json();
    rodadaAtual = 0;
    tamanhoPalavra = dados.tamanho_palavra;
    palpiteAtual = "";

    if (dados.jogador_stats) {
        document.getElementById('vitorias').innerText = dados.jogador_stats.vitorias_totais;
        document.getElementById('sequencia').innerText = dados.jogador_stats.vitorias_seguidas;
    }

    const tabuleiro = document.getElementById('tabuleiro');
    tabuleiro.innerHTML = "";
    for (let i = 0; i < dados.tentativas_maximas; i++) {
        const linhaElemento = document.createElement('div');
        linhaElemento.className = 'linha-tabuleiro';
        linhaElemento.id = `linha-${i}`;
        
        for (let j = 0; j < tamanhoPalavra; j++) {
            const celulaElemento = document.createElement('div');
            celulaElemento.className = 'celula-tabuleiro';
            celulaElemento.id = `celula-${i}-${j}`;
            linhaElemento.appendChild(celulaElemento);
        }
        tabuleiro.appendChild(linhaElemento);
    }

    construirTeclado();
}

function construirTeclado() {
    const teclado = document.getElementById('teclado');
    teclado.innerHTML = "";
    
    const linhas = [
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM"
    ];

    linhas.forEach(linhaLetras => {
        const divLinha = document.createElement('div');
        divLinha.className = 'linha-teclado';
        
        if(linhaLetras === "ZXCVBNM") {
            const btnEnter = document.createElement('button');
            btnEnter.innerText = "ENTER";
            btnEnter.className = 'tecla tecla-acao';
            btnEnter.onclick = enviarTentativa;
            divLinha.appendChild(btnEnter);
        }

        for(let letra of linhaLetras) {
            const btn = document.createElement('button');
            btn.innerText = letra;
            btn.id = `tecla-${letra}`;
            btn.className = 'tecla';
            btn.onclick = () => digitarLetra(letra);
            divLinha.appendChild(btn);
        }

        if(linhaLetras === "ZXCVBNM") {
            const btnDelete = document.createElement('button');
            btnDelete.innerText = "⌫";
            btnDelete.className = 'tecla tecla-acao';
            btnDelete.onclick = apagarLetra;
            divLinha.appendChild(btnDelete);
        }

        teclado.appendChild(divLinha);
    });
}

document.addEventListener('keydown', (e) => {
    if (!jogoAtivo) return;
    if (e.key === "Enter") enviarTentativa();
    else if (e.key === "Backspace") apagarLetra();
    else if (/^[A-Za-z]$/.test(e.key)) digitarLetra(e.key.toUpperCase());
});

function digitarLetra(letra) {
    if (!jogoAtivo) return;
    if (palpiteAtual.length < tamanhoPalavra) {
        palpiteAtual += letra;
        atualizarGridVisual();
    }
}

function apagarLetra() {
    if (!jogoAtivo) return;
    if (palpiteAtual.length > 0) {
        palpiteAtual = palpiteAtual.slice(0, -1);
        atualizarGridVisual();
    }
}

function atualizarGridVisual() {
    for (let i = 0; i < tamanhoPalavra; i++) {
        const celula = document.getElementById(`celula-${rodadaAtual}-${i}`);
        if(celula) {
            celula.innerText = palpiteAtual[i] || "";
        }
    }
}

async function enviarTentativa() {
    if (!jogoAtivo) return;
    if (palpiteAtual.length !== tamanhoPalavra) {
        alert(`A palavra deve conter exatamente ${tamanhoPalavra} letras.`);
        return;
    }

    const response = await fetch('/api/tentativa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ palpite: palpiteAtual })
    });

    const resultado = await response.json();
    if (resultado.erro) return alert(resultado.erro);

    resultado.letras.forEach((infoLetra, index) => {
        const celula = document.getElementById(`celula-${rodadaAtual}-${index}`);
        celula.classList.add(infoLetra.status);
        
        const tecla = document.getElementById(`tecla-${infoLetra.letra}`);
        if (tecla) {
            if (infoLetra.status === "CORRETA") {
                tecla.className = `tecla ${infoLetra.status}`;
            } else if (infoLetra.status === "DESLOCADA" && !tecla.classList.contains("CORRETA")) {
                tecla.className = `tecla ${infoLetra.status}`;
            } else if (infoLetra.status === "INCORRETA" && !tecla.classList.contains("CORRETA") && !tecla.classList.contains("DESLOCADA")) {
                tecla.className = `tecla ${infoLetra.status}`;
            }
        }
    });

    if (resultado.jogador_stats) {
        document.getElementById('vitorias').innerText = resultado.jogador_stats.vitorias_totais;
        document.getElementById('sequencia').innerText = resultado.jogador_stats.vitorias_seguidas;
    }

    rodadaAtual = resultado.rodada_atual;
    palpiteAtual = "";

    if (resultado.fim_de_jogo) {
        finalizarPartida(resultado.ganhou, resultado.resposta);
    }
}

function finalizarPartida(ganhou, resposta) {
    jogoAtivo = false;
    
    if (ganhou) {
        document.getElementById('mensagem').innerText = "🏆 Parabéns! Você acertou a palavra!";
        document.getElementById('mensagem').style.color = "#538d4e";
    } else {
        document.getElementById('mensagem').innerText = `❌ Fim de Jogo! A resposta era: ${resposta}`;
        document.getElementById('mensagem').style.color = "#ff4d4d";
    }
    
    document.getElementById('btn-jogar-novamente').style.display = "inline-block";
    document.getElementById('btn-voltar').style.display = "inline-block";
}