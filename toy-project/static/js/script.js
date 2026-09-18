// 전역 변수로 타이머 ID를 저장
let cardTimer = null;
const cardTimerDuration = 30000;

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
        closeCard(card, body);
        removeAllGrayscale();
        cardTimer = null;
    }, cardTimerDuration);
}

// 펼침 카드가 absolute 오버레이라서 푸터를 덮고 스크롤 공백을 만듦.
// 열린 카드에 본문 높이만큼 여백을 확보해 푸터를 밀어내는 방식으로 해결한다.
function closeCard(card, body) {
    body.classList.remove('active');
    card.classList.remove('active');
    card.parentElement.style.marginBottom = '';
}

function openCardSpacing(card, body) {
    // 펼침 애니메이션(0.3s) 중간에는 높이가 덜 잡히므로 settled 후 재측정한다
    const apply = () => {
        if (!body.classList.contains('active')) return;
        const spill = body.offsetHeight - 10; // top: calc(100% - 10px) 겹침분 제외
        if (spill > 0) card.parentElement.style.marginBottom = spill + 'px';
    };
    requestAnimationFrame(apply);
    setTimeout(apply, 350);
    setTimeout(apply, 900);
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
        closeCard(clickedCard, clickedBody);
        removeAllGrayscale();
    } else {
        // 다른 모든 카드 비활성화
        document.querySelectorAll('.card-body').forEach(body => {
            closeCard(body.closest('.card'), body);
        });
        
        // 현재 카드 활성화
        clickedBody.classList.add('active');
        clickedCard.classList.add('active');
        openCardSpacing(clickedCard, clickedBody);
        
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
    const isLikelyTouchDevice = isMobile();
    document.querySelectorAll('.card').forEach(card => {
        if (isLikelyTouchDevice) {
            // 터치 이벤트 리스너 (모바일 우선)
            card.addEventListener('touchstart', handleTouchStart, { passive: true });
            card.addEventListener('touchmove', handleTouchMove, { passive: true });
            card.addEventListener('touchend', function(e) {
                handleTouchEnd(e, this);
            }, { passive: false });
            return;
        } 
        // 클릭 이벤트 리스너 (데스크톱용)
        card.addEventListener('click', function(e) {
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                e.preventDefault();
                e.stopPropagation();
            }
            toggleCard(this, e);
        });
        
        // 마우스 이벤트 리스너 (데스크톱용)
        card.addEventListener('mouseover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleCard(this);
        });

        card.addEventListener('mouseout', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const body = this.querySelector('.card-body');
            closeCard(this, body);
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
        closeCard(body.closest('.card'), body);
    });
    removeAllGrayscale();
});
