/**
 * Login Vue App
 * Handles user authentication via API
 */
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            form: {
                email: '',
                password: ''
            },
            errors: {},
            isSubmitting: false,
            showPassword: false,
            redirectUrl: ''
        }
    },
    computed: {
        isFormValid() {
            return this.form.email.trim() !== '' &&
                   this.form.password.trim() !== '';
        }
    },
    methods: {
        validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        validateForm() {
            this.errors = {};

            if (!this.form.email.trim()) {
                this.errors.email = "Email обов'язковий";
            } else if (!this.validateEmail(this.form.email)) {
                this.errors.email = 'Невірний формат email';
            }

            if (!this.form.password.trim()) {
                this.errors.password = "Пароль обов'язковий";
            }

            return Object.keys(this.errors).length === 0;
        },

        clearFieldError(field) {
            if (this.errors[field]) {
                delete this.errors[field];
            }
            if (this.errors.general) {
                delete this.errors.general;
            }
        },

        filterEmail(event) {
            const filtered = event.target.value.replace(/[^a-zA-Z0-9@._+-]/g, '');
            this.form.email = filtered;
            event.target.value = filtered;
            this.clearFieldError('email');
        },

        togglePassword() {
            this.showPassword = !this.showPassword;
        },

        async submitLogin() {
            if (!this.validateForm()) {
                return;
            }

            this.isSubmitting = true;
            this.errors = {};

            try {
                const response = await fetch('/api/v1/users/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-CSRFToken': CartHandler.getCSRFToken()
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        email: this.form.email,
                        password: this.form.password
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    if (data.email) {
                        this.errors.email = Array.isArray(data.email) ? data.email[0] : data.email;
                    }
                    if (data.password) {
                        this.errors.password = Array.isArray(data.password) ? data.password[0] : data.password;
                    }
                    if (data.non_field_errors) {
                        this.errors.general = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors;
                    }
                    if (data.detail) {
                        this.errors.general = data.detail;
                    }
                    if (data.error) {
                        this.errors.general = data.error;
                    }

                    if (Object.keys(this.errors).length === 0) {
                        this.errors.general = 'Невірний email або пароль';
                    }

                    this.isSubmitting = false;
                    return;
                }

                // Success - show notification and redirect
                CartHandler.showNotification(data.message || 'Ви успішно увійшли!', 'success');

                // Small delay to show notification
                setTimeout(() => {
                    window.location.href = this.redirectUrl;
                }, 500);

            } catch (error) {
                console.error('Login error:', error);
                this.errors.general = "Помилка з'єднання з сервером";
                this.isSubmitting = false;
            }
        }
    },
    mounted() {
        // Get redirect URL from URL query param (most reliable)
        const urlParams = new URLSearchParams(window.location.search);
        let nextUrl = urlParams.get('next') || '';

        // Fallback to hidden input inside login form only
        if (!nextUrl) {
            const loginForm = document.querySelector('#login-app form');
            const nextInput = loginForm ? loginForm.querySelector('input[name="next"]') : null;
            if (nextInput && nextInput.value) {
                nextUrl = nextInput.value;
            }
        }

        // Don't redirect back to login page
        if (nextUrl && !nextUrl.includes('/login')) {
            this.redirectUrl = nextUrl;
        } else {
            this.redirectUrl = '/';
        }
    }
}).mount('#login-app');
