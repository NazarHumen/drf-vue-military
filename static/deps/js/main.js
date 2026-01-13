document.addEventListener('DOMContentLoaded', function() {

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
