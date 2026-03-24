const ws = new WebSocket(`ws://${location.host}/ws`);

const typedQuery     = document.getElementById("typed-query");
const predictionSeal = document.getElementById("prediction-seal");
const sealValue      = document.getElementById("seal-value");
const sequenceBox    = document.getElementById("sequence-box");
const seqContent     = document.getElementById("sequence-content");
const totalRow       = document.getElementById("total-row");
const totalValue     = document.getElementById("total-value");
const matchBox       = document.getElementById("match-box");
const matchContent   = document.getElementById("match-content");

let lastReveal = false;
let typing = null;

function typeCommand(command, callback) {
    if (typing) clearInterval(typing);
    typedQuery.textContent = "";
    let i = 0;
    typing = setInterval(() => {
        typedQuery.textContent += command[i];
        i += 1;
        if (i >= command.length) {
            clearInterval(typing);
            typing = null;
            if (callback) callback();
        }
    }, 40);
}

function buildSequenceRows(s) {
    let html = "";
    if (s.n1 !== null) html += row("N1  [Subject]", s.n1, "");
    if (s.n2 !== null) html += row("N2  [Subject]", s.n2, "");
    if (s.n3 !== null) html += row("N3  [System] ", s.n3, "system-val");
    if (s.n4 !== null) html += row("N4  [Subject]", s.n4, "");
    if (s.n5 !== null) html += row("N5  [System] ", s.n5, "system-val");
    return html;
}

function row(label, value, cls) {
    return `<div class="seq-row"><span class="seq-label">${label}</span><span class="seq-value ${cls}">${value}</span></div>`;
}

ws.onmessage = (event) => {
    const s = JSON.parse(event.data);

    // Sealed prediction indicator
    if (s.prediction !== null) {
        predictionSeal.classList.remove("hidden");
        sealValue.textContent = s.reveal ? s.prediction : "████████████";
    } else {
        predictionSeal.classList.add("hidden");
    }

    // Progressive sequence table
    if (s.n1 !== null) {
        seqContent.innerHTML = buildSequenceRows(s);
        sequenceBox.classList.remove("hidden");
    } else {
        sequenceBox.classList.add("hidden");
    }

    // Total row (visible on reveal)
    if (s.reveal && s.total !== null) {
        totalValue.textContent = s.total;
        totalRow.classList.remove("hidden");
    } else {
        totalRow.classList.add("hidden");
    }

    // Match box + query animation on first reveal
    if (s.reveal && !lastReveal && s.total !== null) {
        typeCommand(
            "SELECT SUM(n) FROM sequence_log WHERE session = 'LIVE' GROUP BY prediction_id;",
            () => {
                matchContent.innerHTML = `
                    <div>SUM OF SEQUENCE   :  ${s.total}</div>
                    <div>SEALED PREDICTION :  ${s.prediction}</div>
                    <div class="match-line">STATUS            :  &#10003; EXACT MATCH</div>
                `;
                matchBox.classList.remove("hidden");
            }
        );
    }

    if (!s.reveal) {
        matchBox.classList.add("hidden");
        if (typing) { clearInterval(typing); typing = null; }
        typedQuery.textContent = "";
    }

    lastReveal = Boolean(s.reveal);
};
