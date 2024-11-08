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
        const { msg, quote_id } = data;
        console.log(quote_id, msg);
        createMessageElement(msg, quote_id);
    }
}

function createMessageElement(message, quoteId) {
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
            alert('클립보드에 복사되었습니다.');
        });
    });

    // 공유 버튼
    const shareUrl = 'https://a1.mkeasy.kro.kr?r=/chat'
    const shareButton = createButton('share-btn', '<i class="fas fa-share-square"></i>', () => {
        if (navigator.share) {
            navigator.share({
                title: '명언 카드',
                text: message,
                url: shareUrl
            }).then(() => {
                // alert('명언이 공유되었습니다.');
            }).catch((error) => {
                console.error('공유 실패:', error);
            });
        } else {
            alert('공유 기능을 지원하지 않는 브라우저입니다.');
        }
    });

    // 좋아요 버튼
    const likeButton = createButton('like-btn', '<i class="fas fa-thumbs-up"></i>', async () => {
        // alert('좋아요! 이 명언을 좋아합니다.');
        // 추가적인 로직을 여기에 구현할 수 있습니다.
        const response = await fetch('/chat/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quote_id: quoteId })
        });

        if (response.ok) {
            const data = await response.json();
            showLikeNotification(`👍 좋아요! 현재 좋아요: ${data.like_count} 개`, likeButton);
        } else {
            const errorData = await response.json();
            console.error(errorData.detail)
        }
    });

    // 좋아요 알림 메시지 표시 함수
    function showLikeNotification(message, buttonElement) {
        // 알림 요소가 이미 존재하는지 확인
        let notification = document.getElementById('like-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'like-notification';
            document.body.appendChild(notification);
        }

        // 메시지 설정
        notification.innerText = message;
        notification.style.display = 'block';  // 표시
        notification.style.opacity = '1';  // 완전 불투명

        // 버튼의 위치 계산
        const rect = buttonElement.getBoundingClientRect();
        notification.style.position = 'fixed';
        notification.style.top = `${rect.top - 40}px`; // 버튼의 위쪽에서 40px 위에 위치
        notification.style.right = `${window.innerWidth - rect.right + 10}px`; // 버튼의 오른쪽에서 10px 떨어진 위치

        // 3초 후에 사라지도록 설정
        setTimeout(() => {
            notification.style.opacity = '0';  // 점점 투명해짐
            setTimeout(() => {
                notification.style.display = 'none';  // 숨김
            }, 500);  // 투명해지는 시간과 동일
        }, 3000);  // 3초 후
    }

    buttonContainer.appendChild(deleteButton);
    buttonContainer.appendChild(copyButton);
    buttonContainer.appendChild(shareButton);
    buttonContainer.appendChild(likeButton);

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

// 파스텔 색상 목록을 반환하는 함수
function getPastelColors() {
    const colors = [
        [255, 182, 193], [255, 192, 203], [255, 204, 229], [255, 218, 185],
        [255, 240, 245], [255, 228, 225], [255, 228, 196], [255, 218, 185],
        [255, 239, 170], [255, 228, 181], [255, 228, 225], [255, 248, 220],
        [255, 218, 185], [255, 228, 196], [255, 228, 204], [240, 230, 140],
        [255, 239, 172], [250, 240, 190], [245, 222, 179], [255, 239, 204],
        [255, 224, 196], [255, 240, 245], [255, 218, 185], [255, 193, 203],
        [255, 228, 196], [255, 240, 245], [224, 255, 255], [200, 224, 255],
        [204, 204, 255], [224, 224, 255], [240, 240, 255], [230, 230, 250],
        [255, 179, 186], [255, 204, 204], [255, 204, 255], [204, 255, 204],
        [255, 204, 255], [255, 240, 245], [255, 204, 229], [224, 255, 255],
        [240, 230, 140], [255, 250, 205], [255, 228, 181], [255, 218, 185],
        [255, 239, 204], [255, 204, 204], [255, 240, 245], [255, 192, 203],
        [255, 224, 196], [255, 218, 185], [255, 240, 245], [255, 224, 204],
        [255, 240, 245], [255, 228, 205], [255, 240, 245], [255, 218, 203],
        [255, 218, 185], [255, 240, 245], [255, 204, 204], [255, 204, 229],
        [255, 224, 196], [255, 239, 204], [255, 240, 245], [255, 240, 240],
        [200, 224, 255], [204, 204, 255], [224, 224, 255], [240, 240, 255],
        [230, 230, 250], [255, 179, 186], [255, 204, 204], [255, 204, 255],
        [204, 255, 204], [255, 204, 255], [255, 240, 245], [255, 204, 229],
        [224, 255, 255], [240, 230, 140], [255, 250, 205], [255, 228, 181],
        [255, 218, 185], [255, 239, 204], [255, 204, 204], [255, 240, 245],
        [255, 192, 203], [255, 224, 196], [255, 218, 185], [255, 240, 245],
        [255, 224, 204], [255, 240, 245], [255, 228, 205], [255, 240, 245],
        [255, 218, 203], [255, 218, 185], [255, 240, 245], [255, 204, 204],
        [255, 204, 229], [255, 224, 196], [255, 239, 204], [255, 240, 245],
        [255, 240, 240], [200, 224, 255], [204, 204, 255], [224, 224, 255],
        [240, 240, 255], [230, 230, 250], [255, 179, 186], [255, 204, 204],
        [255, 204, 255], [204, 255, 204], [255, 204, 255], [255, 240, 245],
        [255, 204, 229], [224, 255, 255], [240, 230, 140], [255, 250, 205],
        [255, 228, 181], [255, 218, 185], [255, 239, 204], [255, 204, 204],
        [255, 240, 245], [255, 192, 203], [255, 224, 196], [255, 218, 185],
        [255, 240, 245], [255, 224, 204], [255, 240, 245], [255, 228, 205],
        [255, 240, 245], [255, 218, 203], [255, 218, 185], [255, 240, 245],
        [255, 204, 204], [255, 204, 229], [255, 224, 196], [255, 239, 204],
        [255, 240, 245], [255, 240, 240]
    ];
    return colors;    
}

// 파스텔 색상 생성 함수
// function generatePastelColor() {
//     const r = Math.floor(Math.random() * 256);
//     const g = Math.floor(Math.random() * 256);
//     const b = Math.floor(Math.random() * 256);
//     return `rgba(${r}, ${g}, ${b}, 0.6)`; // 투명도 0.6
// }

// 파스텔 색상 생성 함수
function generatePastelColor() {
    const colors = getPastelColors();
    const randomIndex = Math.floor(Math.random() * colors.length);
    const [r, g, b] = colors[randomIndex];
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