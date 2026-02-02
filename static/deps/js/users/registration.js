/**
 * Registration Vue App
 * Handles user registration via API
 */
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            form: {
                first_name: '',
                last_name: '',
                username: '',
                email: '',
                password1: '',
                password2: ''
            },
            errors: {},
            isSubmitting: false,
            showPassword1: false,
            showPassword2: false,
            passwordStrength: 0
        }
    },
    computed: {
        isFormValid() {
            return this.form.first_name.trim() !== '' &&
                   this.form.last_name.trim() !== '' &&
                   this.form.username.trim() !== '' &&
                   this.form.email.trim() !== '' &&
                   this.form.password1.trim() !== '' &&
                   this.form.password2.trim() !== '';
        },
        passwordsMatch() {
            return this.form.password1 === this.form.password2;
        },
        passwordStrengthClass() {
            if (this.passwordStrength === 0) return '';
            if (this.passwordStrength <= 1) return 'bg-danger';
            if (this.passwordStrength <= 2) return 'bg-warning';
            if (this.passwordStrength <= 3) return 'bg-info';
            return 'bg-success';
        },
        passwordStrengthText() {
            if (this.form.password1.length === 0) return '';
            if (this.passwordStrength <= 1) return 'Слабкий';
            if (this.passwordStrength <= 2) return 'Середній';
            if (this.passwordStrength <= 3) return 'Добрий';
            return 'Сильний';
        },
        passwordStrengthPercent() {
            return (this.passwordStrength / 4) * 100;
        }
    },
    methods: {
        validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        validateForm() {
            this.errors = {};

            // First name
            if (!this.form.first_name.trim()) {
                this.errors.first_name = "Ім'я обов'язкове";
            } else if (/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/.test(this.form.first_name)) {
                this.errors.first_name = "Ім'я може містити лише букви";
            }

            // Last name
            if (!this.form.last_name.trim()) {
                this.errors.last_name = "Прізвище обов'язкове";
            } else if (/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/.test(this.form.last_name)) {
                this.errors.last_name = "Прізвище може містити лише букви";
            }

            // Username
            if (!this.form.username.trim()) {
                this.errors.username = "Ім'я користувача обов'язкове";
            } else if (this.form.username.length < 3) {
                this.errors.username = "Мінімум 3 символи";
            } else if (/[^a-zA-Z0-9_]/.test(this.form.username)) {
                this.errors.username = "Тільки латинські букви, цифри та _";
            }

            // Email
            if (!this.form.email.trim()) {
                this.errors.email = "Email обов'язковий";
            } else if (!this.validateEmail(this.form.email)) {
                this.errors.email = "Невірний формат email";
            }

            // Password1
            if (!this.form.password1.trim()) {
                this.errors.password1 = "Пароль обов'язковий";
            } else if (this.form.password1.length < 8) {
                this.errors.password1 = "Мінімум 8 символів";
            }

            // Password2
            if (!this.form.password2.trim()) {
                this.errors.password2 = "Підтвердіть пароль";
            } else if (!this.passwordsMatch) {
                this.errors.password2 = "Паролі не співпадають";
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

        // Input filters
        filterName(event, field) {
            const filtered = event.target.value.replace(/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/g, '');
            this.form[field] = filtered;
            event.target.value = filtered;
            this.clearFieldError(field);
        },

        filterUsername(event) {
            const filtered = event.target.value.replace(/[^a-zA-Z0-9_]/g, '');
            this.form.username = filtered;
            event.target.value = filtered;
            this.clearFieldError('username');
        },

        filterEmail(event) {
            const filtered = event.target.value.replace(/[^a-zA-Z0-9@._+-]/g, '');
            this.form.email = filtered;
            event.target.value = filtered;
            this.clearFieldError('email');
        },

        calculatePasswordStrength() {
            let strength = 0;
            const pwd = this.form.password1;

            if (pwd.length === 0) {
                this.passwordStrength = 0;
                return;
            }

            // Length check
            if (pwd.length >= 8) strength++;
            if (pwd.length >= 12) strength++;

            // Complexity checks
            if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++;
            if (/\d/.test(pwd)) strength++;
            if (/[^a-zA-Z0-9]/.test(pwd)) strength++;

            // Cap at 4
            this.passwordStrength = Math.min(strength, 4);
        },

        togglePassword(field) {
            if (field === 1) {
                this.showPassword1 = !this.showPassword1;
            } else {
                this.showPassword2 = !this.showPassword2;
            }
        },

        async submitRegistration() {
            if (!this.validateForm()) {
                return;
            }

            this.isSubmitting = true;
            this.errors = {};

            try {
                const response = await fetch('/api/v1/users/registration/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-CSRFToken': CartHandler.getCSRFToken()
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        first_name: this.form.first_name,
                        last_name: this.form.last_name,
                        username: this.form.username,
                        email: this.form.email,
                        password1: this.form.password1,
                        password2: this.form.password2
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    // Map API errors to fields
                    Object.keys(data).forEach(key => {
                        if (key === 'non_field_errors') {
                            this.errors.general = Array.isArray(data[key]) ? data[key][0] : data[key];
                        } else if (key === 'detail') {
                            this.errors.general = data[key];
                        } else if (key === 'error') {
                            this.errors.general = data[key];
                        } else {
                            this.errors[key] = Array.isArray(data[key]) ? data[key][0] : data[key];
                        }
                    });

                    CartHandler.showNotification(this.errors.general || 'Помилка реєстрації', 'error');
                    this.isSubmitting = false;
                    return;
                }

                // Success - show notification and redirect
                CartHandler.showNotification(data.message || 'Реєстрація успішна!', 'success');

                // Small delay to show notification
                setTimeout(() => {
                    window.location.href = '/';
                }, 500);

            } catch (error) {
                console.error('Registration error:', error);
                this.errors.general = "Помилка з'єднання з сервером";
                CartHandler.showNotification(this.errors.general, 'error');
                this.isSubmitting = false;
            }
        }
    },
    watch: {
        'form.password1'() {
            this.calculatePasswordStrength();
            this.clearFieldError('password1');
        },
        'form.password2'() {
            this.clearFieldError('password2');
        }
    }
}).mount('#registration-app');
