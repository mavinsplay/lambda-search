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
            
            let startTime = Date.now();
            let lastLoaded = 0;
            let lastTime = startTime;

            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const currentTime = Date.now();
                    const timeElapsed = (currentTime - lastTime) / 1000;
                    const loaded = e.loaded - lastLoaded;
                    
                    if (timeElapsed > 0) {
                        try {
                            const currentSpeed = loaded / timeElapsed;
                            const speedText = formatSpeed(currentSpeed);
                            
                            // Обновляем UI
                            const percent = (e.loaded / e.total) * 100;
                            const progressBar = progress.querySelector('.progress-bar');
                            const percentageDiv = progress.querySelector('.progress-percentage');
                            const speedSpan = progress.querySelector('.upload-speed');
                            const remainingSpan = progress.querySelector('.upload-remaining');
                            const sizeSpan = progress.querySelector('.upload-size');
                            
                            // Проверяем корректность значений
                            if (e.loaded > 0 && e.total > 0) {
                                const loadedSize = formatFileSize(parseInt(e.loaded));
                                const totalSize = formatFileSize(parseInt(e.total));
                                const remainingBytes = Math.max(0, e.total - e.loaded);
                                const remainingSize = formatFileSize(parseInt(remainingBytes));
                                
                                // Обновляем информацию с проверкой
                                progressBar.style.width = percent + '%';
                                percentageDiv.textContent = Math.round(percent) + '%';
                                speedSpan.textContent = speedText;
                                
                                // Расчет оставшегося времени
                                const remaining = remainingBytes / currentSpeed;
                                remainingSpan.textContent = formatTime(remaining);
                                
                                // Обновляем размер с гарантированными значениями
                                sizeSpan.textContent = `${loadedSize} / ${totalSize} (осталось: ${remainingSize})`;
                                
                                // Логируем значения для отладки
                                console.debug('Upload progress:', {
                                    loaded: e.loaded,
                                    total: e.total,
                                    remaining: remainingBytes,
                                    percent: percent
                                });
                            }
                            
                            // Обновляем значения для следующего расчета
                            lastLoaded = e.loaded;
                            lastTime = currentTime;
                        } catch (error) {
                            console.error('Ошибка при обновлении прогресса:', error);
                        }
                    }
                }
            });

            xhr.onload = function() {
                if (xhr.status === 200) {
                    const message = document.createElement('div');
                    message.className = 'success-message';
                    message.textContent = 'База данных успешно загружена';
                    form.appendChild(message);
                    
                    setTimeout(() => {
                        window.location.href = '/admin/search/manageddatabase/';
                    }, 2000);
                }
            };

            // Добавляем обработку ошибок
            xhr.onerror = function() {
                const message = document.createElement('div');
                message.className = 'error-message';
                message.textContent = 'Ошибка загрузки файла';
                form.appendChild(message);
            };

            xhr.open('POST', form.action, true);
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.send(formData);
        });
    });
});

function formatSpeed(bytesPerSecond) {
    const units = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    let value = bytesPerSecond;
    let unitIndex = 0;
    
    while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024;
        unitIndex++;
    }
    
    return `${value.toFixed(1)} ${units[unitIndex]}`;
}

function formatTime(seconds) {
    if (!isFinite(seconds) || seconds < 0) return '--:--';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    try {
        if (!bytes || bytes < 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        
        // Гарантируем, что bytes это число
        bytes = parseInt(bytes);
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        // Проверяем выход за пределы массива
        const sizeIndex = Math.min(i, sizes.length - 1);
        const size = bytes / Math.pow(k, sizeIndex);
        
        return `${size.toFixed(2)} ${sizes[sizeIndex]}`;
    } catch (error) {
        console.error('Ошибка форматирования размера файла:', error);
        return '0 B';
    }
}

function updateProgress(progressId) {
    $.ajax({
        url: '/admin/search/manageddatabase/upload-progress/',
        data: {
            'X-Progress-ID': progressId
        },
        success: function(data) {
            if (data.status === 'success') {
                const progressBar = $('.progress-bar');
                const speedSpan = $('.upload-speed');
                
                progressBar.css('width', data.progress + '%');
                speedSpan.text(formatSpeed(data.speed));
                
                if (data.progress < 100) {
                    setTimeout(() => updateProgress(progressId), 1000);
                }
            }
        }
    });
}

// Генерация уникального ID для отслеживания прогресса
function generateProgressId() {
    return 'progress_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}