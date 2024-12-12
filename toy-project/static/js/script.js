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

function toggleCard(clickedCard) {
    const clickedBody = clickedCard.querySelector('.card-body');
    
    if (isMobile()) {
        // 모바일에서는 현재 카드의 상태를 반전
        if (clickedBody.classList.contains('active')) {
            clickedBody.classList.remove('active');
        } 
        else {
            // 다른 모든 카드는 닫고 현재 카드만 열기
            document.querySelectorAll('.card-body').forEach(body => {
                body.classList.remove('active');
            });
            clickedBody.classList.add('active');
        }
        return;
    } 
    
    // PC에서는 마우스오버 동작 유지
    document.querySelectorAll('.card-body').forEach(body => {
        body.classList.remove('active');
    });
    clickedBody.classList.add('active');
}

document.querySelectorAll('.card').forEach(card => {
    if (isMobile()) {
        // 모바일에서는 터치/클릭 이벤트만 사용
        card.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleCard(this);
        });
    } else {
        // PC에서는 마우스오버/아웃 이벤트 사용
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
    document.querySelectorAll('.card-body').forEach(body => {
        body.classList.remove('active');
    });
});