// 전역 변수로 타이머 ID를 저장
let cardTimer = null;
const cardTimerDuration = 30000;

// bfcache(뒤로가기 복원) 시 구버전 코드로 동작하는 것을 방지
window.addEventListener('pageshow', function (e) {
    if (e.persisted) window.location.reload();
});

// 원격 진단용 (?debug=1 일 때만 화면에 터치 로그 표시, 임시)
const __cardDbgOn = location.search.includes('debug=1');
function __cardDbg(msg) {
    if (!__cardDbgOn) return;
    let el = document.getElementById('__cardDbg');
    if (!el) {
        el = document.createElement('div');
        el.id = '__cardDbg';
        el.style.cssText = 'position:fixed;left:0;bottom:0;z-index:9999;background:rgba(0,0,0,.8);color:#0f0;font-size:11px;max-height:40vh;overflow:auto;padding:6px;white-space:pre-wrap;';
        document.body.appendChild(el);
    }
    el.textContent += msg + '\n';
}
function cardIdx(card) {
    return [...document.querySelectorAll('.card')].indexOf(card);
}
function activeIdx() {
    return [...document.querySelectorAll('.card')].map((c, i) => c.classList.contains('active') ? i : -1).filter(i => i >= 0).join(',');
}

// 터치 식별자별 시작 상태 (다중 터치 시 카드 간 간섭 방지)
let isTouchDevice = false;
const touchStartMap = new Map(); // identifier -> { time, x, y, dragging }

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

// 펼침은 absolute 오버레이: 아래 카드를 밀지 않고 위로 덮는다.
function closeCard(card, body) {
    body.classList.remove('active');
    card.classList.remove('active');
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
        
        // grayscale 효과 적용
        applyGrayscale(clickedCard);
        
        // 타이머 설정
        startCardTimer(clickedCard, clickedBody);
    }
}

// 터치 이벤트 처리 함수
function handleTouchStart(e) {
    isTouchDevice = true;
    const now = Date.now();
    // e.touches[0]은 가장 오래된 터치라서 다중 터치 시 다른 카드 좌표가 섞인다.
    // 새로 닿은 changedTouches를 식별자별로 기록한다.
    for (const touch of e.changedTouches) {
        touchStartMap.set(touch.identifier, {
            time: now, x: touch.clientX, y: touch.clientY, dragging: false
        });
    }
    __cardDbg(`start card=${cardIdx(e.currentTarget)} ids=${[...e.changedTouches].map(t => t.identifier)}`);
}

function handleTouchMove(e) {
    for (const touch of e.changedTouches) {
        const st = touchStartMap.get(touch.identifier);
        if (!st || st.dragging) continue;

        if (Math.hypot(touch.clientX - st.x, touch.clientY - st.y) > 10) {
            st.dragging = true;
            cancelCardTimer();
        }
    }
}

function handleTouchCancel(e) {
    for (const touch of e.changedTouches) {
        touchStartMap.delete(touch.identifier);
    }
    resumeActiveCardTimer();
}

function handleTouchEnd(e, card) {
    if (!isTouchDevice) return;
    const touch = e.changedTouches[0];
    const st = touchStartMap.get(touch.identifier);
    touchStartMap.delete(touch.identifier);
    const dur = st ? Date.now() - st.time : -1;
    const dist = st ? Math.hypot(touch.clientX - st.x, touch.clientY - st.y).toFixed(1) : -1;
    if (!st) { __cardDbg(`end card=${cardIdx(card)} id=${touch.identifier} NO-START`); return; }
    if (st.dragging) {
        __cardDbg(`end card=${cardIdx(card)} id=${touch.identifier} DRAG`);
        resumeActiveCardTimer();
        return;
    }

    // 터치 시간이 너무 길면 무시 (스크롤 등)
    if (dur > 500) { __cardDbg(`end card=${cardIdx(card)} id=${touch.identifier} LONG dur=${dur}`); return; }

    // 터치 이동 거리가 너무 크면 무시 (스크롤 등)
    if (dist > 10) { __cardDbg(`end card=${cardIdx(card)} id=${touch.identifier} MOVED dist=${dist}`); return; }
    
    // 링크나 버튼 클릭은 무시
    const target = e.target;
    if (target.tagName === 'A' || target.tagName === 'BUTTON') return;
    
    e.preventDefault();
    e.stopPropagation();
    
    toggleCard(card, e);
    __cardDbg(`TOGGLE card=${cardIdx(card)} id=${touch.identifier} dur=${dur} dist=${dist} active=[${activeIdx()}]`);
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    const isLikelyTouchDevice = isMobile();
    __cardDbg(`init isMobile=${isLikelyTouchDevice} branch=${isLikelyTouchDevice ? 'touch' : 'mouse'} maxTouch=${navigator.maxTouchPoints} ua=${navigator.userAgent.slice(0, 60)}`);
    document.querySelectorAll('.card').forEach(card => {
        if (isLikelyTouchDevice) {
            // 터치 이벤트 리스너 (모바일 우선)
            card.addEventListener('touchstart', handleTouchStart, { passive: true });
            card.addEventListener('touchmove', handleTouchMove, { passive: true });
            card.addEventListener('touchcancel', handleTouchCancel, { passive: true });
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
