// 전역 변수로 타이머 ID를 저장
let cardTimer = null;
const cardTimerDuration = 3000;

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

function toggleCard(clickedCard, event) {
    if (event && (event.target.tagName === 'A' || event.target.tagName === 'BUTTON')) {
        return;
    }

    const clickedBody = clickedCard.querySelector('.card-body');
    
    // 이전 타이머가 있다면 취소
    if (cardTimer) {
        clearTimeout(cardTimer);
        cardTimer = null;
    }

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
        cardTimer = setTimeout(() => {
            clickedBody.classList.remove('active');
            clickedCard.classList.remove('active');
            removeAllGrayscale();
            cardTimer = null;
        }, cardTimerDuration);
    }
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.card').forEach(card => {
        if (isMobile()) {
            card.addEventListener('click', function(e) {
                if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                    e.preventDefault();
                    e.stopPropagation();
                }
                toggleCard(this, e);
            });
        } else {
            card.addEventListener('mouseover', function() {
                toggleCard(this);
            });

            card.addEventListener('mouseout', function() {
                const body = this.querySelector('.card-body');
                body.classList.remove('active');
                this.classList.remove('active');
                removeAllGrayscale();
            });
        }
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