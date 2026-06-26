let rodadaAtual = 0;
let tamanhoPalavra = 5;

document.getElementById('btn-iniciar').addEventListener('click', iniciarJogo);
document.getElementById('btn-enviar').addEventListener('click', enviarTentativa);

async function iniciarJogo() {
    const modo = document.getElementById('dificuldade').value;

    const response = await fetch('/api/iniciar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modo: modo })
    });

    const dados = await response.json();
    rodadaAtual = 0;
    tamanhoPalavra = dados.tamanho_palavra;

    // Configurar Inputs
    const inputPalpite = document.getElementById('input-palpite');
    inputPalpite.maxLength = tamanhoPalavra;
    inputPalpite.disabled = false;
    inputPalpite.value = "";
    document.getElementById('btn-enviar').disabled = false;
    document.getElementById('mensagem').innerText = "";

    // Construir a View do Tabuleiro Dinamicamente
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
}

async function enviarTentativa() {
    const inputPalpite = document.getElementById('input-palpite');
    const palpite = inputPalpite.value.trim();

    if (palpite.length !== tamanhoPalavra) {
        alert(`A palavra deve conter exatamente ${tamanhoPalavra} letras.`);
        return;
    }

    const response = await fetch('/api/tentativa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ palpite: palpite })
    });

    const resultado = await response.json();

    if (resultado.erro) {
        alert(resultado.erro);
        return;
    }

    // Atualiza a View com o resultado da rodada
    resultado.letras.forEach((infoLetra, index) => {
        const celula = document.getElementById(`celula-${rodadaAtual}-${index}`);
        celula.innerText = infoLetra.letra;
        celula.classList.add(infoLetra.status);
    });

    rodadaAtual = resultado.rodada_atual;
    inputPalpite.value = "";

    // Verifica Condições de Parada
    if (resultado.fim_de_jogo) {
        inputPalpite.disabled = true;
        document.getElementById('btn-enviar').disabled = true;
        
        if (resultado.ganhou) {
            document.getElementById('mensagem').innerText = "🏆 Parabéns! Você acertou a palavra!";
            document.getElementById('mensagem').style.color = "#538d4e";
        } else {
            document.getElementById('mensagem').innerText = `❌ Fim de Jogo! A resposta era: ${resultado.resposta}`;
            document.getElementById('mensagem').style.color = "#ff4d4d";
        }
    }
}