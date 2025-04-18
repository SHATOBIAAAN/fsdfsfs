
document.addEventListener('DOMContentLoaded', function() {
    // Элементы профиля
    const photoInput = document.getElementById('photoInput');
    const photoPreview = document.getElementById('photoPreview');
    const deletePhotoFlag = document.getElementById('deletePhotoFlag');
    const photoUploadArea = document.getElementById('photoUploadArea');
    
    // Элементы модального окна
    const photoUploadModal = document.getElementById('photoUploadModal');
    const closePhotoModalBtn = document.getElementById('closePhotoModalBtn');
    const photoDropArea = document.getElementById('photoDropArea');
    const photoModalPreview = document.getElementById('photoModalPreview');
    const deletePhotoModalBtn = document.getElementById('deletePhotoModalBtn');
    const applyPhotoBtn = document.getElementById('applyPhotoBtn');
    
    // Временное хранение выбранного файла
    let selectedFile = null;
    let photoDeleted = false;
    
    // Показать модальное окно загрузки фото при клике на область фото
    photoUploadArea.addEventListener('click', function() {
        photoUploadModal.classList.add('modal-visible');
        // Обновляем превью в модальном окне на основе текущего фото в профиле
        updateModalPreview();
        // Обновляем состояние кнопки удаления
        updateDeleteButtonState();
    });
    
    // Обновляем превью в модальном окне
    function updateModalPreview() {
        if (selectedFile) {
            // Если уже есть выбранный файл, показываем его
            const reader = new FileReader();
            reader.onload = function(e) {
                photoModalPreview.innerHTML = `
                    <div style="position: relative; width: 200px; height: 200px;">
                        <img src="${e.target.result}" style="width: 100%; height: 100%; border-radius: 16px; object-fit: cover;">
                    </div>
                `;
            };
            reader.readAsDataURL(selectedFile);
        } else if (photoDeleted) {
            // Если фото было удалено
            const nickname = '{{ profile.nickname|default("?") }}';
            const firstLetter = nickname.charAt(0).toUpperCase();
            photoModalPreview.innerHTML = `
                <div style="width: 200px; height: 200px; background-color: #ccc; border-radius: 16px; display: flex; justify-content: center; align-items: center; font-size: 72px; color: #666;">
                    ${firstLetter}
                </div>
            `;
        } else {
            // Иначе показываем текущее фото из профиля
            {% if profile.photo %}
                photoModalPreview.innerHTML = `
                    <div style="position: relative; width: 200px; height: 200px;">
                        <img src="{{ profile.photo.url }}" style="width: 100%; height: 100%; border-radius: 16px; object-fit: cover;">
                    </div>
                `;
            {% else %}
                const nickname = '{{ profile.nickname|default("?") }}';
                const firstLetter = nickname.charAt(0).toUpperCase();
                photoModalPreview.innerHTML = `
                    <div style="width: 200px; height: 200px; background-color: #ccc; border-radius: 16px; display: flex; justify-content: center; align-items: center; font-size: 72px; color: #666;">
                        ${firstLetter}
                    </div>
                `;
            {% endif %}
        }
    }
    
    // Обновление состояния кнопки удаления
    function updateDeleteButtonState() {
        // Показываем кнопку удаления только если есть фото для удаления
        if (({% if profile.photo %}true{% else %}false{% endif %} && !photoDeleted) || selectedFile) {
            deletePhotoModalBtn.style.display = 'block';
        } else {
            deletePhotoModalBtn.style.display = 'none';
        }
    }
    
    // Клик на область загрузки в модальном окне
    photoDropArea.addEventListener('click', function() {
        photoInput.click();
    });
    
    // Обработка выбора файла
    photoInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            selectedFile = this.files[0];
            photoDeleted = false;
            updateModalPreview();
            updateDeleteButtonState();
        }
    });
    
    // Drag & Drop для фото
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        photoDropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        photoDropArea.addEventListener(eventName, function() {
            photoDropArea.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
            photoDropArea.style.borderColor = '#99ff8b';
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        photoDropArea.addEventListener(eventName, function() {
            photoDropArea.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            photoDropArea.style.borderColor = 'white';
        });
    });
    
    photoDropArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files && files[0]) {
            selectedFile = files[0];
            photoDeleted = false;
            updateModalPreview();
            updateDeleteButtonState();
        }
    });
    
    // Удаление фото
    deletePhotoModalBtn.addEventListener('click', function() {
        selectedFile = null;
        photoDeleted = true;
        deletePhotoFlag.value = '1';
        updateModalPreview();
        updateDeleteButtonState();
    });
    
    // Применение изменений
    applyPhotoBtn.addEventListener('click', function() {
        if (selectedFile) {
            // Если выбран новый файл, обновляем превью и скрытый input
            const reader = new FileReader();
            reader.onload = function(e) {
                photoPreview.innerHTML = `<img src="${e.target.result}" alt="Фото профиля" style="width: 160px; height: 160px; border-radius: 16px; object-fit: cover;">`;
            };
            reader.readAsDataURL(selectedFile);
            
            // Создаем объект DataTransfer и добавляем файл
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(selectedFile);
            photoInput.files = dataTransfer.files;
            
            // Снимаем флаг удаления
            deletePhotoFlag.value = '0';
        } else if (photoDeleted) {
            // Если фото было удалено, показываем дефолтное изображение
            const nickname = '{{ profile.nickname|default("?") }}';
            const firstLetter = nickname.charAt(0).toUpperCase();
            photoPreview.innerHTML = `
                <div style="width: 160px; height: 160px; background-color: #ccc; border-radius: 16px; display: flex; justify-content: center; align-items: center; font-size: 36px; color: #666;">
                    ${firstLetter}
                </div>
            `;
            // Очищаем input file
            photoInput.value = '';
            
            // Устанавливаем флаг для удаления фото на сервере
            deletePhotoFlag.value = '1';
        }
        
        // Закрываем модальное окно
        closePhotoModal();
    });
    
    // Закрытие модального окна
    function closePhotoModal() {
        photoUploadModal.classList.remove('modal-visible');
    }
    
    // Обработчики для закрытия модального окна
    closePhotoModalBtn.addEventListener('click', closePhotoModal);
    
    // Закрытие модального окна при клике за его пределами
    photoUploadModal.addEventListener('click', function(e) {
        if (e.target === photoUploadModal) {
            closePhotoModal();
        }
    });
    
    // Закрытие модального окна по клавише Esc
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (photoUploadModal.classList.contains('modal-visible')) {
                closePhotoModal();
            }
        }
    });
    
    // Установка начального состояния кнопки удаления в модальном окне
    updateDeleteButtonState();
    
    // Функция для обработки редактируемых полей
    function setupEditableField(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        const valueEl = field.querySelector('.editable-field-value');
        const inputEl = field.querySelector('.editable-field-input');
        const editIcon = field.querySelector('.edit-icon');
        
        // Показать поле ввода при клике на иконку редактирования
        editIcon.addEventListener('click', function() {
            valueEl.style.display = 'none';
            inputEl.style.display = 'block';
            inputEl.focus();
            editIcon.style.display = 'none';
        });
        
        // Скрыть поле ввода и показать значение при потере фокуса
        inputEl.addEventListener('blur', function() {
            valueEl.textContent = inputEl.value;
            valueEl.style.display = 'inline';
            inputEl.style.display = 'none';
            editIcon.style.display = 'inline';
        });
        
        // Обновить значение при нажатии Enter
        inputEl.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // Предотвращаем отправку формы
                valueEl.textContent = inputEl.value;
                valueEl.style.display = 'inline';
                inputEl.style.display = 'none';
                editIcon.style.display = 'inline';
            }
        });
    }
    
    // Настраиваем редактируемые поля
    setupEditableField('nickname-field');
    setupEditableField('crypto-field');
    
    // Обработка модального окна для удаления аккаунта
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    const deleteAccountModal = document.getElementById('deleteAccountModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    deleteAccountBtn.addEventListener('click', function() {
        deleteAccountModal.classList.add('modal-visible');
        setTimeout(() => {
            document.addEventListener('keydown', escCloseHandler);
        }, 100);
    });
    
    // Обработчик закрытия модального окна
    function closeModal() {
        deleteAccountModal.classList.remove('modal-visible');
        document.removeEventListener('keydown', escCloseHandler);
    }
    
    // Закрытие по клавише Esc
    function escCloseHandler(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    }
    
    cancelDeleteBtn.addEventListener('click', closeModal);
    closeModalBtn.addEventListener('click', closeModal);
    
    // Закрытие модального окна при клике за его пределами
    deleteAccountModal.addEventListener('click', function(e) {
        if (e.target === deleteAccountModal) {
            closeModal();
        }
    });
});
