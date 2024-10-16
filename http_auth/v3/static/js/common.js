window.onload = function() {
    const token = localStorage.getItem("token");
    // 무한 로딩 
    // if (!token) {
    //     window.location.href = "/v3/login"; // 토큰이 없으면 로그인 페이지로 리다이렉트
    // }
};

// 링크 클릭 시 헤더에 토큰 추가
function addTokenToHeaders() {
    const token = localStorage.getItem("token");
    return {
        Authorization: `Bearer ${token}`,
    };
}
