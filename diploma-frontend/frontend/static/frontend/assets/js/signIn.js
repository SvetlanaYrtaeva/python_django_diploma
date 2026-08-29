document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signInForm');

    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('login')?.value;
        const password = document.getElementById('password')?.value;

        console.log('Sign in attempt:', { username });

        if (!username || !password) {
            alert('Введите логин и пароль');
            return;
        }

        try {
            const csrftoken = document.cookie.split('; ')
                .find(row => row.startsWith('csrftoken='))?.split('=')[1];

            const response = await axios.post('/api/sign-in',
                { username, password },
                {
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    }
                }
            );

            console.log('Response status:', response.status);

            if (response.status === 200) {
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Sign in error:', error);

            if (error.response) {
                const data = error.response.data;
                alert(data.detail || 'Ошибка авторизации!');
            } else {
                alert('Ошибка авторизации!');
            }
        }
    });
});