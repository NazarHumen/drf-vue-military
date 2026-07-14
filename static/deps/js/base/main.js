document.addEventListener('DOMContentLoaded', function () {

    // Language switcher: preserve current URL (with query params) after language switch
    function updateLanguageNextInputs() {
        const currentUrl = window.location.pathname + window.location.search;
        document.querySelectorAll('#languageForm input[name="next"], .mobile-nav-lang input[name="next"]').forEach(function (input) {
            input.value = currentUrl;
        });
    }

    // Desktop language dropdown
    const langSwitch = document.getElementById('langSwitch');
    if (langSwitch) {
        const langBtn = document.getElementById('langBtn');

        // Відкрити/закрити меню
        langBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            langSwitch.classList.toggle('open');
        });

        // Language selection -> submit Django set_language form
        langSwitch.querySelectorAll('.lang-menu a').forEach(function (item) {
            item.addEventListener('click', function (e) {
                e.preventDefault();
                const input = document.getElementById('languageInput');
                const form = document.getElementById('languageForm');
                if (input && form) {
                    updateLanguageNextInputs();
                    input.value = this.dataset.code;
                    form.submit();
                }
            });
        });

        // Close when clicking outside the menu
        document.addEventListener('click', function () {
            langSwitch.classList.remove('open');
        });
    }

    // Mobile buttons: submit event fires normally on button click
    document.querySelectorAll('.mobile-nav-lang form').forEach(function (form) {
        form.addEventListener('submit', function () {
            updateLanguageNextInputs();
        });
    });

    // Dropdown toggle for navbar
    document.querySelectorAll('.navbar-dropdown').forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                menu.classList.toggle('show');
            });

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    menu.classList.remove('show');
                }
            });
        }
    });

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileNav = document.getElementById('mobileNav');
    const mobileNavClose = document.getElementById('mobileNavClose');

    if (mobileMenuToggle && mobileNav) {
        // Open mobile menu
        mobileMenuToggle.addEventListener('click', () => {
            mobileNav.classList.add('show');
            document.body.style.overflow = 'hidden';
        });

        // Close mobile menu
        if (mobileNavClose) {
            mobileNavClose.addEventListener('click', () => {
                mobileNav.classList.remove('show');
                document.body.style.overflow = '';
            });
        }

        // Close on clicking outside menu content
        mobileNav.addEventListener('click', (e) => {
            if (e.target === mobileNav) {
                mobileNav.classList.remove('show');
                document.body.style.overflow = '';
            }
        });

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && mobileNav.classList.contains('show')) {
                mobileNav.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    }
});
