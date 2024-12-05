function toggleCard(clickedCard) {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const body = card.querySelector('.card-body');
        body.classList.remove('active');
        if (card === clickedCard) {
            // 클릭한 카드의 상태를 토글
            body.classList.toggle('active');
        }
    });
}

document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', function() {
        toggleCard(this);
    });

    // 마우스 오버 시 active 클래스 추가
    card.addEventListener('mouseover', function() {
        toggleCard(this);
    });

    // 마우스 아웃 시 active 클래스 제거
    card.addEventListener('mouseout', function() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const body = card.querySelector('.card-body');
            body.classList.remove('active');
        });
    });
});