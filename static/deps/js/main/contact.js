document.addEventListener('DOMContentLoaded', function () {
    const {createApp} = Vue;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                form: {
                    last_name: '',
                    first_name: '',
                    email: '',
                    phone: '',
                    comment: ''
                },
                errors: {},
                isSubmitting: false
            }
        },
        methods: {
            // Validation helpers
            validatePhone(phone) {
                const phoneRegex = /^\+?[0-9]{10,15}$/;
                return phoneRegex.test(phone.replace(/\s/g, ''));
            },

            validateEmail(email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(email);
            },

            validateForm() {
                this.errors = {};

                if (!this.form.last_name.trim()) {
                    this.errors.last_name = ["Це поле обов'язкове"];
                } else if (/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/.test(this.form.last_name)) {
                    this.errors.last_name = ["Прізвище може містити лише букви"];
                }

                if (!this.form.first_name.trim()) {
                    this.errors.first_name = ["Це поле обов'язкове"];
                } else if (/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/.test(this.form.first_name)) {
                    this.errors.first_name = ["Ім'я може містити лише букви"];
                }

                if (!this.form.phone.trim()) {
                    this.errors.phone = ["Це поле обов'язкове"];
                } else if (/[^0-9+]/.test(this.form.phone)) {
                    this.errors.phone = ['Номер може містити лише цифри та +'];
                } else if (!this.validatePhone(this.form.phone)) {
                    this.errors.phone = ['Невірний формат номера. Приклад: +380931234567'];
                }

                if (!this.form.email.trim()) {
                    this.errors.email = ["Це поле обов'язкове"];
                } else if (/[^a-zA-Z0-9@.]/.test(this.form.email)) {
                    this.errors.email = ['Email може містити лише англійські букви, цифри та @.'];
                } else if ((this.form.email.match(/@/g) || []).length !== 1) {
                    this.errors.email = ['Email повинен містити один символ @'];
                } else if (!this.validateEmail(this.form.email)) {
                    this.errors.email = ['Невірний формат email'];
                }

                if (!this.form.comment.trim()) {
                    this.errors.comment = ["Це поле обов'язкове"];
                }

                return Object.keys(this.errors).length === 0;
            },

            clearFieldError(field) {
                if (this.errors[field]) {
                    delete this.errors[field];
                }
            },

            // Input filters
            filterName(event, field) {
                const filtered = event.target.value.replace(/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/g, '');
                this.form[field] = filtered;
                event.target.value = filtered;
                this.clearFieldError(field);
            },

            filterPhone(event) {
                const filtered = event.target.value.replace(/[^0-9+]/g, '');
                this.form.phone = filtered;
                event.target.value = filtered;
                this.clearFieldError('phone');
            },

            filterEmail(event) {
                const filtered = event.target.value.replace(/[^a-zA-Z0-9@.]/g, '');
                this.form.email = filtered;
                event.target.value = filtered;
                this.clearFieldError('email');
            },

            async submitForm() {
                if (!this.validateForm()) {
                    return;
                }

                this.isSubmitting = true;

                try {
                    const response = await fetch('/api/v1/main/feedback/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'X-CSRFToken': CartHandler.getCSRFToken()
                        },
                        body: JSON.stringify(this.form)
                    });
                    const data = await response.json();
                    if (response.ok) {
                        CartHandler.showNotification(
                            data.message, 'success'
                        );
                        this.resetForm();
                    } else {
                        this.errors = data;
                    }
                } catch (error) {
                    CartHandler.showNotification(
                        "Помилка з'єднання", 'error'
                    );
                } finally {
                    this.isSubmitting = false;
                }
            },

            resetForm() {
                this.form = {
                    last_name: '',
                    first_name: '',
                    phone: '',
                    email: '',
                    comment: ''
                };
                this.errors = {};
            }
        }
    }).mount('#contact-app');
});
