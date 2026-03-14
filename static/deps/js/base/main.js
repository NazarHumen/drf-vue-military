document.addEventListener('DOMContentLoaded', function() {

    // Language switcher: preserve current URL (with query params) after language switch
    function updateLanguageNextInputs() {
        const currentUrl = window.location.pathname + window.location.search;
        document.querySelectorAll('#languageForm input[name="next"], .mobile-nav-lang input[name="next"]').forEach(function(input) {
            input.value = currentUrl;
        });
    }

    // Desktop select: onchange="this.form.submit()" bypasses the submit event,
    // so we override it with a proper change listener
    const langSelect = document.getElementById('languageSelect');
    if (langSelect) {
        langSelect.onchange = function() {
            updateLanguageNextInputs();
            this.form.submit();
        };
    }

    // Mobile buttons: submit event fires normally on button click
    document.querySelectorAll('.mobile-nav-lang form').forEach(function(form) {
        form.addEventListener('submit', function() {
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
