document.addEventListener('DOMContentLoaded', function () {
    // Мобильное меню
    const menuToggle = document.getElementById('mobileMenuToggle')
    const mainNav = document.getElementById('mainNav')

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', function () {
            this.classList.toggle('open')
            mainNav.classList.toggle('open')

            // Блокируем/разблокируем скролл на странице при открытом меню
            if (mainNav.classList.contains('open')) {
                document.body.style.overflow = 'hidden'
            } else {
                document.body.style.overflow = ''
            }
        })

        // Закрываем меню при клике на ссылку в мобильном меню
        const navLinks = mainNav.querySelectorAll('a')
        navLinks.forEach(link => {
            link.addEventListener('click', function () {
                // Не закрываем меню для якорных ссылок или ссылок на ту же страницу
                // (Хотя в вашем меню вроде таких нет, но на всякий случай)
                if (
                    link.getAttribute('href') !== '#' &&
                    !link.href.startsWith(window.location.href + '#')
                ) {
                    menuToggle.classList.remove('open')
                    mainNav.classList.remove('open')
                    document.body.style.overflow = ''
                }
            })
        })

        // Закрываем меню при клике вне меню
        document.addEventListener('click', function (event) {
            if (
                !mainNav.contains(event.target) &&
                !menuToggle.contains(event.target) &&
                mainNav.classList.contains('open')
            ) {
                menuToggle.classList.remove('open')
                mainNav.classList.remove('open')
                document.body.style.overflow = ''
            }
        })
    }

    // Можно добавить сюда другой JS код для базового шаблона, если он появится
})
