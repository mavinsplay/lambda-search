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
                            // Расчет скорости как в рабочем примере
                            const currentSpeed = loaded / timeElapsed;
                            const speedText = formatSpeed(currentSpeed);
                            
                            // Получаем элементы UI
                            const progressBar = progress.querySelector('.progress-bar');
                            const percentageDiv = progress.querySelector('.progress-percentage');
                            const speedSpan = progress.querySelector('.upload-speed');
                            const remainingSpan = progress.querySelector('.upload-remaining');
                            const sizeSpan = progress.querySelector('.upload-size');
                            
                            // Расчет процента загрузки
                            const percent = (e.loaded / e.total) * 100;
                            
                            // Обновляем UI с проверками
                            if (progressBar) progressBar.style.width = percent + '%';
                            if (percentageDiv) percentageDiv.textContent = Math.round(percent) + '%';
                            if (speedSpan) speedSpan.textContent = speedText;
                            
                            // Расчет оставшегося времени как в рабочем примере
                            const remainingBytes = e.total - e.loaded;
                            const remaining = remainingBytes / currentSpeed;
                            if (remainingSpan) remainingSpan.textContent = formatTime(remaining);
                            
                            // Обновляем информацию о размере аналогично скорости
                            if (sizeSpan) {
                                const loadedSize = formatFileSize(e.loaded);
                                const totalSize = formatFileSize(e.total);
                                const remainingSize = formatFileSize(remainingBytes);
                                sizeSpan.textContent = `${loadedSize} / ${totalSize} (осталось: ${remainingSize})`;
                            }
                            
                            // Детальное логирование для отладки
                            console.debug('Upload progress details:', {
                                loaded: e.loaded,
                                total: e.total,
                                percent: percent,
                                speed: currentSpeed,
                                remaining: remaining,
                                elapsed: timeElapsed
                            });

                            // Обновляем значения для следующего расчета
                            lastLoaded = e.loaded;
                            lastTime = currentTime;
                        } catch (error) {
                            console.error('Ошибка обновления прогресса:', error);
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

            // Улучшаем обработку ошибок
            xhr.onerror = function(error) {
                console.error('Ошибка загрузки файла:', error);
                const message = document.createElement('div');
                message.className = 'error-message';
                message.textContent = `Ошибка загрузки файла: ${error.type}`;
                form.appendChild(message);
            };

            xhr.onabort = function() {
                console.error('Загрузка файла прервана');
                const message = document.createElement('div');
                message.className = 'error-message';
                message.textContent = 'Загрузка файла была прервана';
                form.appendChild(message);
            };

            xhr.ontimeout = function() {
                console.error('Превышено время ожидания загрузки');
                const message = document.createElement('div');
                message.className = 'error-message';
                message.textContent = 'Превышено время ожидания загрузки';
                form.appendChild(message);
            };

            // Добавляем таймаут для XHR
            xhr.timeout = 3600000; // 1 час в миллисекундах

            // Улучшаем обработку ошибок сервера
            xhr.onreadystatechange = function() {
                console.debug('XHR состояние:', {
                    readyState: xhr.readyState,
                    status: xhr.status,
                    statusText: xhr.statusText
                });

                if (xhr.readyState === 4) {
                    if (xhr.status !== 200) {
                        let errorMessage = `Ошибка сервера: ${xhr.status} ${xhr.statusText}\n`;
                        
                        // Добавляем информацию о размере загруженного файла
                        const uploadedSize = formatFileSize(lastLoaded);
                        errorMessage += `Загружено: ${uploadedSize}\n`;

                        // Пытаемся получить детали ошибки
                        if (xhr.responseText) {
                            try {
                                const response = JSON.parse(xhr.responseText);
                                errorMessage += `Детали: ${response.message || response.error || xhr.responseText}`;
                            } catch (e) {
                                errorMessage += `Ответ сервера: ${xhr.responseText}`;
                            }
                        }

                        // Для ошибки 502 добавляем специфичную информацию
                        if (xhr.status === 502) {
                            errorMessage += '\nВозможные причины:\n';
                            errorMessage += '- Превышен лимит времени загрузки\n';
                            errorMessage += '- Превышен лимит размера файла\n';
                            errorMessage += '- Проблемы с подключением к серверу';
                        }

                        console.error(errorMessage);

                        // Создаем сообщение об ошибке в UI
                        const message = document.createElement('div');
                        message.className = 'error-message';
                        message.textContent = errorMessage;
                        form.appendChild(message);

                        // Дополнительная отладочная информация
                        console.debug('Заголовки запроса:', xhr.getAllResponseHeaders());
                    }
                }
            };

            // Добавляем обработчик прогресса загрузки с отладкой
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    console.debug('Прогресс загрузки:', {
                        loaded: formatFileSize(e.loaded),
                        total: formatFileSize(e.total),
                        percent: ((e.loaded / e.total) * 100).toFixed(2) + '%'
                    });
                }
            };

            // Добавляем обработчик начала загрузки
            xhr.upload.onloadstart = function() {
                console.debug('Начало загрузки файла');
            };

            // Добавляем обработчик завершения загрузки
            xhr.upload.onloadend = function() {
                console.debug('Завершение загрузки файла');
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