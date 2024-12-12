function isMobile() {
    // 1. UserAgent 검사
    const userAgent = navigator.userAgent.toLowerCase();
    const mobileKeywords = [
        'android', 'iphone', 'ipod', 'ipad', 'windows phone',
        'webos', 'blackberry', 'mobile', 'opera mini'
    ];
    
    // 2. 터치 기능 확인
    const hasTouchScreen = (
        ('ontouchstart' in window) ||
        (navigator.maxTouchPoints > 0) ||
        (navigator.msMaxTouchPoints > 0)
    );
    
    // 3. 화면 크기 및 방향 확인
    const isPortrait = window.innerHeight > window.innerWidth;
    
    // 모바일 키워드 체크
    const isMobileDevice = mobileKeywords.some(keyword => 
        userAgent.includes(keyword)
    );
    
    // 최종 판단: 모바일 UA이거나 (터치스크린이면서 세로모드)
    return isMobileDevice || (hasTouchScreen && isPortrait);
}

function toggleCard(clickedCard) {
    const cards = document.querySelectorAll('.card');
    const clickedBody = clickedCard.querySelector('.card-body');

    if (isMobile()) {
        // 모바일에서는 클릭한 카드만 토글
        clickedBody.classList.toggle('active');
    } else {
        // PC에서는 다른 카드는 닫고 클릭한 카드만 열기
        cards.forEach(card => {
            const body = card.querySelector('.card-body');
            body.classList.remove('active');
        });
        clickedBody.classList.add('active');
    }
}

document.querySelectorAll('.card').forEach(card => {
    // 클릭 이벤트
    card.addEventListener('click', function() {
        if (isMobile()) {
            toggleCard(this);
        }
    });

    // PC에서만 마우스오버/아웃 이벤트 적용
    card.addEventListener('mouseover', function() {
        if (!isMobile()) {
            toggleCard(this);
        }
    });

    card.addEventListener('mouseout', function() {
        if (!isMobile()) {
            const body = this.querySelector('.card-body');
            body.classList.remove('active');
        }
    });
});

// 화면 크기 변경 시 모든 카드 닫기
window.addEventListener('resize', function() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const body = card.querySelector('.card-body');
        body.classList.remove('active');
    });
});