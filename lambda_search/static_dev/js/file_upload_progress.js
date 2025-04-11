document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        const form = input.closest('form');
        const progress = input.nextElementSibling;
        
        if (!form || !progress) return;

        input.addEventListener('change', function() {
            progress.style.display = 'block';
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const xhr = new XMLHttpRequest();
            const formData = new FormData(form);

            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    const progressBar = progress.querySelector('.progress-bar');
                    progressBar.style.width = percent + '%';
                }
            });

            xhr.onload = function() {
                if (xhr.status === 200) {
                    // Редирект на список баз данных
                    window.location.href = '/admin/search/manageddatabase/';
                }
            };

            xhr.open('POST', form.action, true);
            
            // Получаем CSRF токен
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            
            xhr.send(formData);
        });
    });
});