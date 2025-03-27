window.addEventListener('load', function() {
    'use strict';

    function updateProgressBars() {
        const progressContainers = document.querySelectorAll('.progress-container');
        
        progressContainers.forEach(function(container) {
            const taskId = container.dataset.taskId;
            
            fetch('/search/task-progress/?task_id=' + taskId)
                .then(response => response.json())
                .then(data => {
                    const progressBar = container.querySelector('.progress-bar-fill');
                    const progressText = container.querySelector('.progress-text');
                    const description = container.querySelector('span:last-child');
                    
                    // Получаем данные из структуры JSON
                    const percent = data.percent || 0;
                    const current = data.current || 0;
                    const total = data.total || 0;
                    const desc = data.description || '';
                    
                    // Обновляем полосу прогресса
                    progressBar.style.width = percent + '%';
                    progressBar.style.backgroundColor = 
                        percent == 100 ? '#28a745' : 
                        percent > 0 ? '#007bff' : '#ffc107';
                    
                    // Обновляем текст прогресса
                    progressText.textContent = `${Math.floor(percent)}% (${current}/${total})`;
                    
                    // Обновляем описание
                    if (description) {
                        description.textContent = desc;
                    }
                })
                .catch(error => {
                    console.error('Error receiving progress:', error);
                });
        });
    }

    // Обновляем прогресс каждые 2 секунды
    setInterval(updateProgressBars, 2000);
});