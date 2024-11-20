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
});