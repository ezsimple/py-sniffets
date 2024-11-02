const COUNTDOWN = 3; // 카운트다운 시간 설정
const MAX_ROW = 3; // 최대 li 개수 설정
const HEARTBEAT_INTERVAL = 30000; // 30초마다 heartbeat 체크
const PING_TIMEOUT = 5000; // 5초 동안 응답이 없으면 연결 끊김으로 간주

let socket;
let heartbeatInterval;

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function connectSocket() {
    const user_id = getCookie('user_id');
    socket = new WebSocket(WS_SERVER + '?user_id='+user_id);

    socket.onopen = function() {
        sendMessage();
        startHeartbeat();
    };

    socket.onmessage = function(event) {
        handleIncomingMessage(event);
    };

    socket.onerror = function(error) {
        console.error("WebSocket 오류:", error);
        clearInterval(heartbeatInterval);
        disableQuoteButton();
    };

    socket.onclose = function() {
        console.warn("WebSocket 연결 종료");
        reconnectSocket();
    };
}

function reconnectSocket() {
    console.warn("WebSocket 재연결 시도...");
    let delay = 1000
    const attemptReconnect = setInterval(() => {
        if (socket.readyState === WebSocket.CLOSED) {
            connectSocket();
            delay *= 2; // 지연 시간 두 배 증가
        } else {
            clearInterval(attemptReconnect); // 성공적으로 연결되면 인터벌 정지
        }
    }, delay);
}

function handleIncomingMessage(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'heartbeat') {
        startHeartbeat();
        return;
    }

    // 메시지가 비어있지 않은 경우에만 li 요소 생성
    if (data.msg && data.msg.trim()) {
        createMessageElement(data.msg);
    }
}

function createMessageElement(message) {
    const li = document.createElement('li');
    const pastelColor = generatePastelColor();
    li.style.backgroundColor = pastelColor;
    li.style.color = getFontColor(pastelColor);

    const messageContainer = document.createElement('div');
    messageContainer.className = 'message-container';
    messageContainer.innerHTML = `${message.replace(/\n/g, '<br>')}`;

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'button-container';

    // 삭제 버튼
    const deleteButton = createButton('delete-btn', '<i class="fas fa-trash-alt"></i>', () => {
        li.remove();
    });

    // 클립보드 복사 버튼
    const copyButton = createButton('copy-btn', '<i class="fas fa-copy"></i>', () => {
        navigator.clipboard.writeText(message).then(() => {
            alert('명언이 클립보드에 복사되었습니다.');
        });
    });

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

function createButton(className, innerHTML, onClick) {
    const button = document.createElement('button');
    button.className = className;
    button.innerHTML = innerHTML;
    button.onclick = onClick;
    return button;
}

// heartbeat 시작
function sendPing() {
    if (socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({ type: 'ping' }));
}

function startHeartbeat() {
    clearInterval(heartbeatInterval);
    heartbeatInterval = setInterval(() => {
        sendPing();
    }, HEARTBEAT_INTERVAL);
}

// sendMessage 함수 정의
const sendMessage = function() {
    if (socket.readyState !== WebSocket.OPEN) {
        reconnectSocket();
        return;
    }

    // WebSocket이 열린 경우에만 메시지를 전송
    const liCount = document.querySelectorAll('#messages li').length;
    const reqMessage = {'MAX_ROW': MAX_ROW, 'liCount' : liCount.toString()}
    socket.send(JSON.stringify(reqMessage)); // liCount를 문자열로 변환하여 전송

    // 카운트다운 설정
    let countdown = COUNTDOWN;
    const button = disableQuoteButton();
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

// UI 관련 설정
function setupUIHandlers() {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault(); // 기본 동작 방지
            sendMessage(); // 메시지 전송 함수 호출
        }
    });

    document.addEventListener('selectstart', function(event) {
        event.preventDefault(); // 텍스트 선택 방지
    });

    document.addEventListener('dblclick', function(event) {
        event.preventDefault(); // 기본 동작 방지 (텍스트 선택 방지)
        sendMessage(); // 메시지 전송 함수 호출
    });

    document.getElementById('quoteButton').addEventListener('click', sendMessage);
}

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

// 초기화
setupUIHandlers();
connectSocket();