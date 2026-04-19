var board = null
var game = new Chess()
var $status = $('#game-status')
var $agentLog = $('#agent-log')
var $llmTime = $('#llm-time')
var $humanTime = $('#human-time')
var humanMoveStartTime = Date.now()

$('#dev-mode-toggle').on('change', function() {
    if(this.checked) {
        $('#debug-panel').removeClass('hidden');
    } else {
        $('#debug-panel').addClass('hidden');
    }
});

function fetchDebugLogs() {
    fetch('/api/debug_logs')
        .then(res => res.json())
        .then(data => {
            $('#debug-log').text(data.prompt || "No prompt generated yet...");
        });
}

$('#download-pgn-btn').on('click', function() {
    const btn = $(this);
    const originalText = btn.text();
    btn.text('Saving...');
    
    fetch('/api/download_pgn')
        .then(res => res.json())
        .then(data => {
            btn.text(originalText);
            if(data.success) {
                // Successfully saved
            }
        })
        .catch(err => {
            btn.text(originalText);
        });
});

function onDragStart (source, piece, position, orientation) {
  if (game.game_over()) return false
  if (piece.search(/^b/) !== -1) return false
}

function onDrop (source, target) {
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q'
  })

  if (move === null) return 'snapback'

  let timeTaken = ((Date.now() - humanMoveStartTime) / 1000).toFixed(1);
  $humanTime.text(timeTaken + "s");

  const uciMove = source + target + (move.flags.includes('p') ? 'q' : '');
  
  $status.text("Gemma is thinking...");
  $('#loading-spinner').removeClass('hidden');

  fetch('/api/human_move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ move: uciMove })
  })
  .then(res => res.json())
  .then(data => {
      if(data.success) {
          triggerLLMMove();
      } else {
          game.undo();
          board.position(game.fen());
      }
  })
  .catch(err => {
      game.undo();
      board.position(game.fen());
  });
}

function triggerLLMMove() {
    $('#loading-spinner').removeClass('hidden');
    $status.text("Gemma is thinking...");
    $('.system-msg').addClass('hidden');
    
    const streamContainer = document.createElement('div');
    streamContainer.className = "stream-container";
    const textSpan = document.createElement('span');
    textSpan.className = "stream-text";
    streamContainer.appendChild(textSpan);
    $agentLog.append(streamContainer);
    
    const logEl = $agentLog[0];
    logEl.scrollTop = logEl.scrollHeight;

    // Refresh debug logs shortly after request starts
    setTimeout(fetchDebugLogs, 1000);

    const eventSource = new EventSource('/api/llm_move_stream');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
            const logEl = $agentLog[0];
            // Check if user is scrolled to the bottom (within 50px tolerance)
            const isScrolledToBottom = logEl.scrollHeight - logEl.scrollTop <= logEl.clientHeight + 50;

            // Append streaming text
            let escaped = $('<div>').text(data.content).html();
            escaped = escaped.replace(/\n/g, '<br>');
            textSpan.innerHTML += escaped;
            
            // Smart auto-scroll
            if (isScrolledToBottom) {
                logEl.scrollTop = logEl.scrollHeight;
            }
        } 
        else if (data.type === 'success') {
            eventSource.close();
            $('#loading-spinner').addClass('hidden');
            
            const from = data.move.substring(0, 2);
            const to = data.move.substring(2, 4);
            const promotion = data.move.length === 5 ? data.move[4] : undefined;
            
            game.move({from: from, to: to, promotion: promotion});
            board.position(game.fen());
            
            $llmTime.text(data.time + "s");
            
            const moveHeader = document.createElement('div');
            moveHeader.innerHTML = `<strong style="color: #a78bfa; display: block; margin-bottom: 0.5rem;">Move Selected: ${data.move}</strong>`;
            streamContainer.insertBefore(moveHeader, textSpan);
            
            updateStatus(data.game_over);
            humanMoveStartTime = Date.now();
        }
        else if (data.type === 'error') {
            eventSource.close();
            $('#loading-spinner').addClass('hidden');
            $status.text("Error: " + data.message);
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
        $('#loading-spinner').addClass('hidden');
        $status.text("Stream connection lost.");
    };
}

function onSnapEnd () {
  board.position(game.fen())
}

function updateStatus (isGameOver) {
  var statusHTML = ''
  if (game.in_checkmate() || isGameOver) {
    statusHTML = 'Game over!'
  } else if (game.in_draw()) {
    statusHTML = 'Game drawn'
  } else {
    statusHTML = "Your turn (White)"
    if (game.in_check()) {
      statusHTML += ' - Check!'
    }
  }
  $status.html(statusHTML)
}

var config = {
  draggable: true,
  position: 'start',
  pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd
}
board = Chessboard('board', config)
updateStatus(false)
