// Lista atualizada com palavras acentuadas e com Ç
const LISTA_PALAVRAS = [
    "BARÃO", "ÂNIMO", "PÁREO", "CAÇAR", "MAÇÃS", 
    "AÇÕES", "ÓRFÃO", "VISÃO", "SAÚDE", "CAFÉS",
    "TERMO", "JOGOS", "VERDE", "LETRA", "PLANO",
    "MUNDO", "TEMPO", "NOITE", "FORTE", "IDEIA"
];

const TENTATIVAS_MAXIMAS = 6;
const TAMANHO_PALAVRA = 5;

const LAYOUT_TECLADO = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "APAGAR"]
];

let palavraSecreta = "";
let linhaAtual = 0;
let letraAtual = 0;
let palpiteAtual = "";
let jogoFinalizado = false;

const grid = document.getElementById("grid");
const msgDisplay = document.getElementById("mensagem");
const btnReiniciar = document.getElementById("btn-reiniciar");
const tecladoContainer = document.getElementById("teclado");

// FUNÇÃO CRUCIAL: Remove acentos e transforma Ç em C para fins de comparação
function normalizar(texto) {
    return texto
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "") // Remove acentos titis, agudos, circunflexos...
        .replace(/Ç/g, "C")              // Transforma Ç em C
        .toUpperCase();
}

function iniciarJogo() {
    const indiceAleatorio = Math.floor(Math.random() * LISTA_PALAVRAS.length);
    palavraSecreta = LISTA_PALAVRAS[indiceAleatorio];
    
    linhaAtual = 0;
    letraAtual = 0;
    palpiteAtual = "";
    jogoFinalizado = false;
    
    msgDisplay.innerText = "Digite uma palavra e aperte Enter!";
    btnReiniciar.style.display = "none";
    
    grid.innerHTML = "";
    criarTabuleiro();
    criarTeclado();
}

function criarTabuleiro() {
    for (let i = 0; i < TENTATIVAS_MAXIMAS; i++) {
        const linha = document.createElement("div");
        linha.className = "linha";
        linha.id = `linha-${i}`;
        
        for (let j = 0; j < TAMANHO_PALAVRA; j++) {
            const caixaLetra = document.createElement("div");
            caixaLetra.className = "letra";
            caixaLetra.id = `linha-${i}-letra-${j}`;
            linha.appendChild(caixaLetra);
        }
        grid.appendChild(linha);
    }
}

function criarTeclado() {
    tecladoContainer.innerHTML = "";
    LAYOUT_TECLADO.forEach(linha => {
        const divLinha = document.createElement("div");
        divLinha.className = "linha-teclado";
        
        linha.forEach(letra => {
            const botao = document.createElement("button");
            botao.className = "tecla";
            botao.innerText = letra;
            botao.id = `tecla-${letra}`;
            
            if (letra === "ENTER" || letra === "APAGAR") {
                botao.classList.add("grande");
            }
            
            botao.addEventListener("click", () => lidarComEntrada(letra));
            divLinha.appendChild(botao);
        });
        tecladoContainer.appendChild(divLinha);
    });
}

function lidarComEntrada(tecla) {
    if (jogoFinalizado) return;

    if (tecla === "BACKSPACE" || tecla === "APAGAR") {
        if (letraAtual > 0) {
            letraAtual--;
            const caixa = document.getElementById(`linha-${linhaAtual}-letra-${letraAtual}`);
            caixa.innerText = "";
            palpiteAtual = palpiteAtual.slice(0, -1);
        }
        return;
    }

    if (tecla === "ENTER") {
        if (palpiteAtual.length === TAMANHO_PALAVRA) {
            verificarPalpite();
        } else {
            exibirMensagem("A palavra deve ter 5 letras!");
        }
        return;
    }

    // O jogador só consegue digitar de A a Z normalizado (sem acento/ç nativo)
    if (/^[A-Z]$/.test(tecla) && letraAtual < TAMANHO_PALAVRA) {
        const caixa = document.getElementById(`linha-${linhaAtual}-letra-${letraAtual}`);
        caixa.innerText = tecla;
        palpiteAtual += tecla;
        letraAtual++;
    }
}

document.addEventListener("keydown", (e) => {
    lidarComEntrada(e.key.toUpperCase());
});

function verificarPalpite() {
    const palavraSecretaNorm = normalizar(palavraSecreta);
    const palpiteNorm = palpiteAtual; // Já vem limpo do teclado
    
    let secretaAux = palavraSecretaNorm;
    let statusLinha = Array(TAMANHO_PALAVRA).fill("errado");

    // Primeira passada: marcar os verdes (comparando as versões limpas)
    for (let i = 0; i < TAMANHO_PALAVRA; i++) {
        const caixa = document.getElementById(`linha-${linhaAtual}-letra-${i}`);
        
        if (palpiteNorm[i] === palavraSecretaNorm[i]) {
            statusLinha[i] = "correto";
            // REVELAÇÃO: Coloca o caractere real da palavra secreta (com acento/ç) no visor!
            caixa.innerText = palavraSecreta[i]; 
            secretaAux = secretaAux.replace(palpiteNorm[i], "_");
        }
    }

    // Segunda passada: marcar os amarelos e cinzas nos blocos e teclado
    for (let i = 0; i < TAMANHO_PALAVRA; i++) {
        const caixa = document.getElementById(`linha-${linhaAtual}-letra-${i}`);
        const letraDigitada = palpiteNorm[i];

        if (statusLinha[i] === "correto") {
            caixa.classList.add("correto");
            atualizarStatusTecla(letraDigitada, "correto");
            continue;
        }

        if (secretaAux.includes(letraDigitada)) {
            caixa.classList.add("deslocado");
            atualizarStatusTecla(letraDigitada, "deslocado");
            secretaAux = secretaAux.replace(letraDigitada, "_");
        } else {
            caixa.classList.add("errado");
            atualizarStatusTecla(letraDigitada, "errado");
        }
    }

    // Validação da vitória por meio das strings limpas
    if (palpiteNorm === palavraSecretaNorm) {
        exibirMensagem(`Parabéns! Você acertou: ${palavraSecreta} 🎉`);
        finalizarJogo();
        return;
    }

    linhaAtual++;
    letraAtual = 0;
    palpiteAtual = "";

    if (linhaAtual === TENTATIVAS_MAXIMAS) {
        exibirMensagem(`Fim de jogo! A palavra era: ${palavraSecreta}`);
        finalizarJogo();
    }
}

function atualizarStatusTecla(letra, status) {
    const botao = document.getElementById(`tecla-${letra}`);
    if (!botao) return;

    if (botao.classList.contains("correto")) return;
    if (botao.classList.contains("deslocado") && status === "errado") return;

    botao.classList.remove("correto", "deslocado", "errado");
    botao.classList.add(status);
}

function exibirMensagem(texto) {
    msgDisplay.innerText = texto;
}

function finalizarJogo() {
    jogoFinalizado = true;
    btnReiniciar.style.display = "block";
}

btnReiniciar.addEventListener("click", iniciarJogo);

iniciarJogo();