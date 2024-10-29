const COUNTDOWN = 30; // 카운트다운 시간 설정
const MAX_ROW = 5; // 최대 li 개수 설정
const socket = new WebSocket("ws://localhost:4444/chat/ws");

socket.onopen = function() {
    sendMessage(); // WebSocket이 열릴 때 한 번 호출
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    // 메시지가 비어있지 않은 경우에만 li 요소 생성
    if (data.msg.trim()) {
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
        document.getElementById('messages').appendChild(li); // li를 메시지 목록에 추가

        // 테두리 애니메이션 추가
        li.classList.add('border-fade'); // 테두리 애니메이션 클래스 추가

        // li 개수 체크 및 초과 시 제거
        const messagesList = document.getElementById('messages');
        if (messagesList.children.length > MAX_ROW) {
            const firstChild = messagesList.firstChild;
            firstChild.classList.add('shatter'); // 부서지는 효과 추가
            setTimeout(() => {
                messagesList.removeChild(firstChild); // 애니메이션 후 제거
            }, 500); // 500ms 후에 제거
        }

        setTimeout(() => {
            messagesList.scrollTop = messagesList.scrollHeight;
        }, 1000); // 1초후에 스크롤을 가장 아래로 이동
    }
};

socket.onerror = function(error) {
    console.error("WebSocket 오류:", error);
};

// sendMessage 함수 정의
const sendMessage = function() {
    const button = document.getElementById('quoteButton');
    button.disabled = true;
    button.style.backgroundColor = 'gray';

    // WebSocket이 열린 경우에만 메시지를 전송
    if (socket.readyState === WebSocket.OPEN) {
        const message = ''; // 메시지 내용
        socket.send(message);

        // 카운트다운 설정
        let countdown = COUNTDOWN;
        const interval = setInterval(() => {
            button.textContent = `오늘의 명언 (${countdown}s)`;
            countdown--;

            // 카운트다운이 끝나면 원래 상태로 복원
            if (countdown < 0) {
                clearInterval(interval);
                button.textContent = `오늘의 명언 (${COUNTDOWN}s)`;
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
        document.getElementById('quoteButton').click(); // 버튼 클릭
    }
});

// 버튼 클릭 이벤트 핸들러 추가
document.getElementById('quoteButton').addEventListener('click', sendMessage);

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
    return brightness > 186 ? 'black' : 'white'; // 밝기 기준 조정
}