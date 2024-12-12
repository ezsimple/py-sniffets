function hideAllElements() {
        // 모든 요소를 숨기는 함수
        // 모든 요소를 선택
        const allElements = document.querySelectorAll('*');
        
        // 각 요소에 대해 display: none; 적용
        allElements.forEach(element => {
                element.style.display = 'none';
        });
}

function showAllElements() {
        // 모든 요소를 다시 보이게 하는 함수
        // 모든 요소를 선택
        const allElements = document.querySelectorAll('*');

        // 각 요소에 대해 display 속성을 원래 상태로 적용
        allElements.forEach(element => {
                element.style.display = '';  // ""로 설정하면 원래의 display 속성이 유지됨
        });
}

function isKakaoBrowser() {
    return /KAKAOTALK/i.test(navigator.userAgent);
}

function getRedirectPath() {
    const params = new URLSearchParams(window.location.search);
    return params.get('r'); // 'redirect' 파라미터의 값을 가져옴
}

// 페이지가 로드되면 자동으로 실행됩니다.
    hideAllElements()
window.onload = function() {
    const redirectPath = getRedirectPath(); // redirect 파라미터 값 가져오기
    if (!redirectPath) {
                showAllElements();
                return;
            }

    let targetUrl = new URL(window.location.origin); // 현재 도메인으로 생성
    targetUrl.pathname = redirectPath; // redirectPath를 경로로 설정

    if (isKakaoBrowser()) {
        targetUrl = 'kakaotalk://web/openExternal?url=' + encodeURIComponent(targetUrl.href);
    } else {
        targetUrl = targetUrl.href; // 일반 URL을 사용
    }

    location.href = targetUrl; // 리다이렉트
}