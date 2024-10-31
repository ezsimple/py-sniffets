const COUNTDOWN = 3; // 카운트다운 시간 설정
const MAX_ROW = 3; // 최대 li 개수 설정
const socket = new WebSocket(WS_SERVER);
const HEARTBEAT_INTERVAL = 30000; // 30초마다 heartbeat 체크
const PING_TIMEOUT = 5000; // 5초 동안 응답이 없으면 연결 끊김으로 간주

let heartbeatInterval;

function reconnectWebsocket() {
    console.warn("WebSocket 재연결 시도...");
    const newSocket = new WebSocket(WS_SERVER);
    newSocket.onopen = function() {
        socket = newSocket;
        sendMessage();
    };
    newSocket.onmessage = socket.onmessage;
    newSocket.onerror = socket.onerror;
    socket = newSocket;
}

socket.onopen = function() {
    sendMessage();
};

// heartbeat 시작
function sendPing() {
    if (socket.readyState !== WebSocket.OPEN)
        return;
    socket.send(JSON.stringify({ type: 'ping' }));
}

function startHeartbeat() {
    clearInterval(heartbeatInterval);
    heartbeatInterval = setInterval(() => {
        sendPing();
    }, HEARTBEAT_INTERVAL);
}

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'heartbeat') {
        startHeartbeat();
        return;
    }

    // 메시지가 비어있지 않은 경우에만 li 요소 생성
    if (data.msg && data.msg.trim()) {
        const li = document.createElement('li');
        const pastelColor = generatePastelColor();
        li.style.backgroundColor = pastelColor;
        li.style.color = getFontColor(pastelColor);

        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';
        messageContainer.innerHTML = `${data.msg.replace(/\n/g, '<br>')}`;

        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'button-container';

        // 삭제 버튼
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-btn';
        deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>'; // 삭제 아이콘
        deleteButton.onclick = function() {
            li.remove();
        };

        // 클립보드 복사 버튼
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-btn';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>'; // 복사 아이콘
        copyButton.onclick = function() {
            navigator.clipboard.writeText(data.msg).then(() => {
                alert('명언이 클립보드에 복사되었습니다.');
            });
        };

        buttonContainer.appendChild(deleteButton);
        buttonContainer.appendChild(copyButton);

        li.appendChild(messageContainer);
        li.appendChild(buttonContainer);
        
        const messagesList = document.getElementById('messages');
        messagesList.insertBefore(li, messagesList.firstChild);

        // li 개수 체크 및 초과 시 제거
        if (messagesList.children.length > MAX_ROW) {
            const lastChild = messagesList.lastChild;
            lastChild.classList.add('shatter');
            setTimeout(() => {
                messagesList.removeChild(lastChild);
            }, 500);
        }
    }
};

socket.onerror = function(error) {
    console.error("WebSocket 오류:", error);
    clearInterval(heartbeatInterval);
    disableQuoteButton();
};

// sendMessage 함수 정의
const sendMessage = function() {
    const button = disableQuoteButton();

    if (socket.readyState !== WebSocket.OPEN) {
        reconnectWebsocket();
        return;
    }

    // WebSocket이 열린 경우에만 메시지를 전송
    const liCount = document.querySelectorAll('#messages li').length;
    socket.send(liCount.toString()); // liCount를 문자열로 변환하여 전송

    // 카운트다운 설정
    let countdown = COUNTDOWN;
    const interval = setInterval(() => {
        button.textContent = `오늘의 띵언 (${countdown}s)`;
        countdown--;

        // 카운트다운이 끝나면 원래 상태로 복원
        if (countdown < 0) {
            clearInterval(interval);
            button.textContent = `오늘의 띵언 (${COUNTDOWN}s)`;
            button.disabled = false;
            button.style.backgroundColor = '#4a90e2'; // 원래 색상으로 변경
        }
    }, 1000);
};

// 스페이스, 엔터키 입력되면 자동
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault(); // 기본 동작 방지
        sendMessage(); // 메시지 전송 함수 호출
    }
});

// 두 번 클릭하면 자동 명언 생성
document.addEventListener('dblclick', function() {
    sendMessage(); // 메시지 전송 함수 호출
});

// 버튼 클릭 이벤트 핸들러 추가
document.getElementById('quoteButton').addEventListener('click', sendMessage);

// 오늘의 명언 버튼 비활성화
function disableQuoteButton() {
    const button = document.getElementById('quoteButton');
    button.disabled = true;
    button.style.backgroundColor = 'gray';
    return button;
}

// 파스텔 색상 생성 함수
function generatePastelColor() {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    return `rgba(${r}, ${g}, ${b}, 0.6)`; // 투명도 0.6
}

// 폰트 색상 결정 함수
function getFontColor(backgroundColor) {
    const rgb = backgroundColor.match(/\d+/g);
    const brightness = (parseInt(rgb[0]) * 0.299 + parseInt(rgb[1]) * 0.587 + parseInt(rgb[2]) * 0.114);
    return brightness > 120 ? 'black' : 'white'; // 밝기 기준 조정
}
