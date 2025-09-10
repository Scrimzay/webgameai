async function renderBoard() {
    const res = await fetch('/state');
    const state = await res.json();
    const boardEl = document.getElementById('board');
    boardEl.innerHTML = '';
    
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            if (state.board[i][j] === 1) {
                cell.textContent = 'X';
                cell.classList.add('x');
            } else if (state.board[i][j] === -1) {
                cell.textContent = 'O';
                cell.classList.add('o');
            }
            cell.onclick = () => makeMove(i, j);
            boardEl.appendChild(cell);
        }
    }

    const statusEl = document.getElementById('status');
    if (state.winner === 1) {
        statusEl.textContent = 'Player X wins!';
    } else if (state.winner === -1) {
        statusEl.textContent = 'Player O wins!';
    } else if (isBoardFull(state.board)) {
        statusEl.textContent = 'Draw!';
    } else {
        statusEl.textContent = `Player ${state.current_player === 1 ? 'X' : 'O'}'s turn`;
    }
}

function isBoardFull(board) {
    return board.every(row => row.every(cell => cell !== 0));
}

async function makeMove(row, col) {
    const res = await fetch(`/move/${row}/${col}`, { method: 'POST' });
    if (!res.ok) {
        const error = await res.json();
        alert(error.error || 'Invalid move!');
        return;
    }
    await renderBoard();
}

async function newGame() {
    await fetch('/new-game');
    await renderBoard();
}

// Initial render
renderBoard();