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
    
    const isPortrait = window.innerHeight > window.innerWidth;
    const isMobileDevice = mobileKeywords.some(keyword => 
        userAgent.includes(keyword)
    );
    
    return isMobileDevice || (hasTouchScreen && isPortrait);
}

function toggleCard(clickedCard) {
    if (isMobile()) {
        // 모바일에서는 클릭한 카드만 토글
        const clickedBody = clickedCard.querySelector('.card-body');
        clickedBody.classList.toggle('active');
    } else {
        // PC에서는 기존 동작 유지
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const body = card.querySelector('.card-body');
            if (card === clickedCard) {
                body.classList.add('active');
            } else {
                body.classList.remove('active');
            }
        });
    }
}

document.querySelectorAll('.card').forEach(card => {
    // 클릭 이벤트
    card.addEventListener('click', function(e) {
        if (isMobile()) {
            e.preventDefault(); // 기본 동작 방지
            toggleCard(this);
        }
    });

    // PC에서만 마우스오버/아웃 이벤트 적용
    if (!isMobile()) {
        card.addEventListener('mouseover', function() {
            toggleCard(this);
        });

        card.addEventListener('mouseout', function() {
            const body = this.querySelector('.card-body');
            body.classList.remove('active');
        });
    }
});

// 화면 크기 변경 시 모든 카드 닫기
window.addEventListener('resize', function() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const body = card.querySelector('.card-body');
        body.classList.remove('active');
    });
});