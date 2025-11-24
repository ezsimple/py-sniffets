// 전역 변수로 타이머 ID를 저장
let cardTimer = null;
const cardTimerDuration = 5000;

// 터치 이벤트 관련 변수
let touchStartTime = 0;
let touchStartPosition = { x: 0, y: 0 };
let isTouchDevice = false;
let isTouchDragging = false;

function cancelCardTimer() {
    if (cardTimer) {
        clearTimeout(cardTimer);
        cardTimer = null;
    }
}

function startCardTimer(card, body) {
    cancelCardTimer();
    cardTimer = setTimeout(() => {
        body.classList.remove('active');
        card.classList.remove('active');
        removeAllGrayscale();
        cardTimer = null;
    }, cardTimerDuration);
}

function resumeActiveCardTimer() {
    const activeCard = document.querySelector('.card.active');
    if (!activeCard) {
        cancelCardTimer();
        return;
    }
    const activeBody = activeCard.querySelector('.card-body.active');
    if (!activeBody) return;
    startCardTimer(activeCard, activeBody);
}

function isMobile() {
    const userAgent = navigator.userAgent.toLowerCase();
    const mobileKeywords = [
        'android', 'iphone', 'ipod', 'ipad', 'windows phone',
        'webos', 'blackberry', 'mobile', 'opera mini'
    ];
    
    const hasTouchScreen = (
        ('ontouchstart' in window) ||
        (navigator.maxTouchPoints > 0) ||
        (navigator.msMaxTouchPoints > 0)
    );
    
    const isMobileDevice = mobileKeywords.some(keyword => 
        userAgent.includes(keyword)
    );
    
    return isMobileDevice || hasTouchScreen;
}

function applyGrayscale(activeCard) {
    // 모든 카드에 대해 처리
    document.querySelectorAll('.card').forEach(card => {
        if (card !== activeCard) {
            card.classList.add('grayscale');
        } else {
            card.classList.remove('grayscale');
        }
    });
}

function removeAllGrayscale() {
    document.querySelectorAll('.card').forEach(card => {
        card.classList.remove('grayscale');
    });
}

function toggleCard(clickedCard, event = null) {
    if (event && (event.target.tagName === 'A' || event.target.tagName === 'BUTTON')) {
        return;
    }

    const clickedBody = clickedCard.querySelector('.card-body');
    
    // 이전 타이머가 있다면 취소
    cancelCardTimer();

    if (clickedBody.classList.contains('active')) {
        clickedBody.classList.remove('active');
        clickedCard.classList.remove('active');
        removeAllGrayscale();
    } else {
        // 다른 모든 카드 비활성화
        document.querySelectorAll('.card-body').forEach(body => {
            body.classList.remove('active');
            body.closest('.card').classList.remove('active');
        });
        
        // 현재 카드 활성화
        clickedBody.classList.add('active');
        clickedCard.classList.add('active');
        
        // grayscale 효과 적용
        applyGrayscale(clickedCard);
        
        // 타이머 설정
        startCardTimer(clickedCard, clickedBody);
    }
}

// 터치 이벤트 처리 함수
function handleTouchStart(e) {
    isTouchDevice = true;
    touchStartTime = Date.now();
    const touch = e.touches[0];
    touchStartPosition = { x: touch.clientX, y: touch.clientY };
    isTouchDragging = false;
}

function handleTouchMove(e) {
    if (!isTouchDevice || isTouchDragging) return;
    
    const touch = e.touches[0];
    const currentPosition = { x: touch.clientX, y: touch.clientY };
    
    const distance = Math.sqrt(
        Math.pow(currentPosition.x - touchStartPosition.x, 2) + 
        Math.pow(currentPosition.y - touchStartPosition.y, 2)
    );
    
    if (distance > 10) {
        isTouchDragging = true;
        cancelCardTimer();
    }
}

function handleTouchEnd(e, card) {
    if (!isTouchDevice) return;
    if (isTouchDragging) {
        isTouchDragging = false;
        resumeActiveCardTimer();
        return;
    }
    
    const touchEndTime = Date.now();
    const touchDuration = touchEndTime - touchStartTime;
    
    // 터치 시간이 너무 길면 무시 (스크롤 등)
    if (touchDuration > 500) return;
    
    const touch = e.changedTouches[0];
    const touchEndPosition = { x: touch.clientX, y: touch.clientY };
    
    // 터치 이동 거리가 너무 크면 무시 (스크롤 등)
    const distance = Math.sqrt(
        Math.pow(touchEndPosition.x - touchStartPosition.x, 2) + 
        Math.pow(touchEndPosition.y - touchStartPosition.y, 2)
    );
    
    if (distance > 10) return;
    
    // 링크나 버튼 클릭은 무시
    const target = e.target;
    if (target.tagName === 'A' || target.tagName === 'BUTTON') return;
    
    e.preventDefault();
    e.stopPropagation();
    
    toggleCard(card, e);
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.card').forEach(card => {
        // 터치 이벤트 리스너 (모바일 우선)
        card.addEventListener('touchstart', handleTouchStart, { passive: true });
        card.addEventListener('touchmove', handleTouchMove, { passive: true });
        card.addEventListener('touchend', function(e) {
            handleTouchEnd(e, this);
        }, { passive: false });
        
        // 클릭 이벤트 리스너 (데스크톱용)
        card.addEventListener('click', function(e) {
            // 터치 디바이스에서는 클릭 이벤트 무시 (중복 방지)
            if (isTouchDevice) return;
            
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                e.preventDefault();
                e.stopPropagation();
            }
            toggleCard(this, e);
        });
        
        // 마우스 이벤트 리스너 (데스크톱용)
        card.addEventListener('mouseover', function() {
            // 터치 디바이스에서는 마우스 이벤트 무시
            if (isTouchDevice) return;
            toggleCard(this);
        });

        card.addEventListener('mouseout', function() {
            // 터치 디바이스에서는 마우스 이벤트 무시
            if (isTouchDevice) return;
            const body = this.querySelector('.card-body');
            body.classList.remove('active');
            this.classList.remove('active');
            removeAllGrayscale();
        });
    });
});

// 화면 크기 변경 시 모든 카드 닫기와 타이머 취소
window.addEventListener('resize', function() {
    if (cardTimer) {
        clearTimeout(cardTimer);
        cardTimer = null;
    }
    document.querySelectorAll('.card-body').forEach(body => {
        body.classList.remove('active');
        body.closest('.card').classList.remove('active');
    });
    removeAllGrayscale();
});
