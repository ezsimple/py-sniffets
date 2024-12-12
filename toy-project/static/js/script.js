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

function toggleCard(clickedCard, event) {
    if (event && (event.target.tagName === 'A' || event.target.tagName === 'BUTTON')) {
        return;
    }

    const clickedBody = clickedCard.querySelector('.card-body');
    
    if (isMobile()) {
        if (clickedBody.classList.contains('active')) {
            clickedBody.classList.remove('active');
        } else {
            document.querySelectorAll('.card-body').forEach(body => {
                body.classList.remove('active');
            });
            clickedBody.classList.add('active');
        }
    } else {
        document.querySelectorAll('.card-body').forEach(body => {
            body.classList.remove('active');
        });
        clickedBody.classList.add('active');
    }
}

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
        });
    }
});

// 화면 크기 변경 시 모든 카드 닫기
window.addEventListener('resize', function() {
    document.querySelectorAll('.card-body').forEach(body => {
        body.classList.remove('active');
    });
});