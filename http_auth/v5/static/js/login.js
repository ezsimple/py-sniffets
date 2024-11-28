document.getElementById('loginForm').onsubmit = function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch(this.action, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "/v1/login";
        } else {
            const formBox = document.querySelector('.form-box');
            formBox.classList.add('shake');
            formBox.classList.add('wine');

            setTimeout(() => { 
                formBox.classList.remove('shake'); 
                formBox.classList.remove('wine');
            }, 500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
};