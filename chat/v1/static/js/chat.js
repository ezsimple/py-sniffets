const COUNTDOWN = 3; // 카운트다운 시간 설정
const MAX_ROW = 3; // 최대 li 개수 설정
const socket = new WebSocket(WS_SERVER);
const HEARTBEAT_INTERVAL = 30000; // 30초마다 heartbeat 체크
const PING_TIMEOUT = 5000; // 5초 동안 응답이 없으면 연결 끊김으로 간주

socket.onopen = function() {
    sendMessage(); // WebSocket이 열릴 때 한 번 호출
};

// heartbeat 시작
let heartbeatInterval;
function sendPing() {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'ping' }));
        // console.log('Ping sent to server.');
    }
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

        // 동적으로 파스텔 색상 배경 생성
        const pastelColor = generatePastelColor();
        li.style.backgroundColor = pastelColor;

        // 폰트 색상 조정
        li.style.color = getFontColor(pastelColor);

        // 메시지 표시용 div
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';
        messageContainer.innerHTML = `${data.msg.replace(/\n/g, '<br>')}`;

        // 버튼 컨테이너 생성
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

        // 버튼 컨테이너에 버튼 추가
        buttonContainer.appendChild(deleteButton); // 삭제 버튼을 버튼 컨테이너에 추가
        buttonContainer.appendChild(copyButton); // 복사 버튼을 버튼 컨테이너에 추가

        // li에 메시지와 버튼 컨테이너 추가
        li.appendChild(messageContainer); // 메시지 영역 추가
        li.appendChild(buttonContainer); // 버튼 컨테이너 추가
        
        const messagesList = document.getElementById('messages');
        
        // 최신 li를 맨 앞에 추가
        messagesList.insertBefore(li, messagesList.firstChild); // 최신 메시지를 가장 위에 추가

        // li 개수 체크 및 초과 시 제거
        if (messagesList.children.length > MAX_ROW) {
            const lastChild = messagesList.lastChild; // 마지막 li 요소
            lastChild.classList.add('shatter'); // 부서지는 효과 추가
            setTimeout(() => {
                messagesList.removeChild(lastChild); // 애니메이션 후 제거
            }, 500); // 500ms 후에 제거
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

    // WebSocket이 열린 경우에만 메시지를 전송
    if (socket.readyState === WebSocket.OPEN) {
        const liCount = document.querySelectorAll('#messages li').length;
        socket.send(liCount);

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
        }, 1000); // 1초마다 업데이트
    } else {
        console.error("WebSocket이 열리지 않았습니다.");
    }
};


// 스페이스, 엔터키 입력되면 자동
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault(); // 기본 동작 방지
        sendMessage(); // 메시지 전송 함수 호출
    }
});

// 두번 클릭하면 자동 명언 생성
document.addEventListener('dblclick', function() {
    sendMessage(); // 메시지 전송 함수 호출
});

// 버튼 클릭 이벤트 핸들러 추가
document.getElementById('quoteButton').addEventListener('click', sendMessage);

// 오늘의 명언버튼 비활성화
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
    // RGB 값을 추출
    const rgb = backgroundColor.match(/\d+/g);
    const brightness = (parseInt(rgb[0]) * 0.299 + parseInt(rgb[1]) * 0.587 + parseInt(rgb[2]) * 0.114);
    // 밝은 색상에서는 검은색, 어두운 색상에서는 흰색
    return brightness > 120 ? 'black' : 'white'; // 밝기 기준 조정
}