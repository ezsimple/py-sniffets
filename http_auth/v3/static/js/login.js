document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/v3/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            username: username,
            password: password,
        }),
    });

    try {
        if (response.ok) {
            const data = await response.json();
            console.log("로그인 성공:", data.access_token);
            localStorage.setItem("token", data.access_token);
            // window.location.href = "/v3/files"; // 로그인 성공 시 이동
        } else {
            // 400오류, HTTP
            const errorData = await response.json();
            alert(`로그인 실패: ${errorData.detail}`);
        }
    } catch (error) {
        alert(error)
    }
});
