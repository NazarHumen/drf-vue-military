/**
 * Profile Vue App
 * Handles user profile editing only
 */
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            // User profile data
            user: {
                id: null,
                first_name: '',
                last_name: '',
                username: '',
                email: '',
                phone_number: '',
                image: null
            },

            // Profile form
            form: {
                first_name: '',
                last_name: '',
                username: '',
                phone_number: ''
            },

            // Avatar
            avatarPreview: null,
            avatarFile: null,

            // UI state
            isLoadingProfile: true,
            isSavingProfile: false,

            // Errors
            errors: {},
            profileError: null
        }
    },
    computed: {
        hasProfileChanges() {
            return this.form.first_name !== this.user.first_name ||
                   this.form.last_name !== this.user.last_name ||
                   this.form.username !== this.user.username ||
                   this.form.phone_number !== (this.user.phone_number || '') ||
                   this.avatarFile !== null;
        },
        avatarUrl() {
            if (this.avatarPreview) return this.avatarPreview;
            if (this.user.image) return this.user.image;
            return '/static/deps/images/baseavatar.jpg';
        }
    },
    methods: {
        async fetchProfile() {
            this.isLoadingProfile = true;
            this.profileError = null;

            try {
                const response = await fetch('/api/v1/users/profile/', {
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin'
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.replace('/api/v1/users/login/?next=/api/v1/users/profile/');
                        return;
                    }
                    throw new Error('Помилка завантаження профілю');
                }

                const data = await response.json();
                this.user = data.user;

                // Initialize form with user data
                this.form.first_name = this.user.first_name || '';
                this.form.last_name = this.user.last_name || '';
                this.form.username = this.user.username || '';
                this.form.phone_number = this.user.phone_number || '';

            } catch (error) {
                console.error('Profile fetch error:', error);
                this.profileError = error.message;
            } finally {
                this.isLoadingProfile = false;
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

        filterPhone(event) {
            let value = event.target.value.replace(/[^\d+]/g, '');
            // Ensure + is only at beginning
            if (value.indexOf('+') > 0) {
                value = '+' + value.replace(/\+/g, '');
            }
            // Limit length
            if (value.startsWith('+380')) {
                value = value.slice(0, 13);
            } else {
                value = value.slice(0, 16);
            }
            this.form.phone_number = value;
            event.target.value = value;
            this.clearFieldError('phone_number');
        },

        clearFieldError(field) {
            if (this.errors[field]) {
                delete this.errors[field];
            }
        },

        // Avatar handling
        onAvatarSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Validate file type
            if (!file.type.startsWith('image/')) {
                CartHandler.showNotification('Виберіть файл зображення', 'error');
                event.target.value = '';
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                CartHandler.showNotification('Файл занадто великий (макс. 5MB)', 'error');
                event.target.value = '';
                return;
            }

            this.avatarFile = file;

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                this.avatarPreview = e.target.result;
            };
            reader.readAsDataURL(file);
        },

        // Validation
        validateProfile() {
            this.errors = {};

            if (!this.form.first_name.trim()) {
                this.errors.first_name = "Ім'я обов'язкове";
            }
            if (!this.form.last_name.trim()) {
                this.errors.last_name = "Прізвище обов'язкове";
            }
            if (!this.form.username.trim()) {
                this.errors.username = "Username обов'язковий";
            }
            if (this.form.phone_number && !/^\+?\d{10,15}$/.test(this.form.phone_number.replace(/\s/g, ''))) {
                this.errors.phone_number = 'Невірний формат телефону';
            }

            return Object.keys(this.errors).length === 0;
        },

        // Save profile
        async saveProfile() {
            if (!this.validateProfile()) return;

            this.isSavingProfile = true;

            try {
                let body;
                let headers = {
                    'X-CSRFToken': CartHandler.getCSRFToken()
                };

                // Use FormData if avatar is being uploaded
                if (this.avatarFile) {
                    body = new FormData();
                    body.append('first_name', this.form.first_name);
                    body.append('last_name', this.form.last_name);
                    body.append('username', this.form.username);
                    if (this.form.phone_number) {
                        body.append('phone_number', this.form.phone_number);
                    }
                    body.append('image', this.avatarFile);
                    // Don't set Content-Type for FormData
                } else {
                    headers['Content-Type'] = 'application/json';
                    body = JSON.stringify({
                        first_name: this.form.first_name,
                        last_name: this.form.last_name,
                        username: this.form.username,
                        phone_number: this.form.phone_number || null
                    });
                }

                const response = await fetch('/api/v1/users/profile/', {
                    method: 'PATCH',
                    headers,
                    credentials: 'same-origin',
                    body
                });

                const data = await response.json();

                if (!response.ok) {
                    Object.keys(data).forEach(key => {
                        this.errors[key] = Array.isArray(data[key]) ? data[key][0] : data[key];
                    });
                    throw new Error('Validation failed');
                }

                // Update local state
                this.user = data.user;
                this.avatarFile = null;
                this.avatarPreview = null;

                // Reset file input
                const fileInput = document.getElementById('id_image');
                if (fileInput) fileInput.value = '';

                CartHandler.showNotification(data.message || 'Профіль оновлено', 'success');

            } catch (error) {
                if (error.message !== 'Validation failed') {
                    CartHandler.showNotification('Помилка збереження', 'error');
                }
            } finally {
                this.isSavingProfile = false;
            }
        }
    },
    mounted() {
        this.fetchProfile();
    }
}).mount('#profile-app');
