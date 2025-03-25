document.addEventListener("DOMContentLoaded", function () {
    var progressUrl = "{{ progress_url }}";
    // Инициализируем прогресс-бар с помощью функции из django-celery-progress.
    // Функция должна опрашивать progressUrl и вызывать onProgress с meta-данными.
    CeleryProgressBar.initProgressBar(progressUrl, {
      onProgress: function(data) {
        // meta-данные задачи должны содержать processed, total и percent
        var percent = data.percent || 0;
        var processed = data.processed || 0;
        var total = data.total || 0;
        document.getElementById("progress-bar").style.width = percent + "%";
        document.getElementById("progress-text").innerText = processed + " строк зашифровано (" + percent + "%)";
      },
      onSuccess: function(result) {
        document.getElementById("progress-bar").style.width = "100%";
        document.getElementById("progress-text").innerText = result.processed + " строк зашифровано (100%)";
      }
    });
  });