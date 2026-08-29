document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signUpForm');
    
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name')?.value;
        const username = document.getElementById('username')?.value;
        const password = document.getElementById('password')?.value;
        
        console.log('Sign up attempt:', { name, username });
        
        if (!username || !password) {
            alert('Введите логин и пароль');
            return;
        }
        
        if (password.length < 6) {
            alert('Пароль должен быть не менее 6 символов');
            return;
        }
        
        try {
            const csrftoken = document.cookie.split('; ')
                .find(row => row.startsWith('csrftoken='))?.split('=')[1];
            
            const response = await axios.post('/api/sign-up', 
                { name, username, password },
                {
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            console.log('Response status:', response.status);
            
            if (response.status === 201) {
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Sign up error:', error);
            
            if (error.response) {
                const data = error.response.data;
                alert(data.detail || 'Ошибка регистрации!');
            } else {
                alert('Ошибка регистрации!');
            }
        }
    });
});