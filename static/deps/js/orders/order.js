const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            // Cart state
            items: [],
            totalPrice: 0,
            totalPriceUsd: 0,
            totalQuantity: 0,
            isLoadingCart: true,
            cartError: null,

            // Form state
            form: {
                first_name: '',
                last_name: '',
                phone_number: '',
                email: '',
                requires_delivery: '1',
                delivery_address: '',
                payment_on_get: '0'
            },

            // Form validation errors
            errors: {},

            // Submission state
            isSubmitting: false,
            submitError: null,
            submitSuccess: false
        }
    },
    computed: {
        showDeliveryAddress() {
            return this.form.requires_delivery === '1';
        },
        isFormValid() {
            return this.form.first_name.trim() !== '' &&
                   this.form.last_name.trim() !== '' &&
                   this.form.phone_number.trim() !== '' &&
                   this.form.email.trim() !== '' &&
                   (!this.showDeliveryAddress || this.form.delivery_address.trim() !== '') &&
                   this.items.length > 0;
        }
    },
    methods: {
        async fetchCart() {
            this.isLoadingCart = true;
            this.cartError = null;

            try {
                const data = await CartHandler.getCart();
                if (data) {
                    this.items = data.items || [];
                    this.totalPrice = data.total_price || 0;
                    this.totalPriceUsd = data.total_price_usd || 0;
                    this.totalQuantity = data.total_quantity || 0;
                }
            } catch (error) {
                console.error('Error fetching cart:', error);
                this.cartError = 'Не вдалося завантажити кошик';
            } finally {
                this.isLoadingCart = false;
            }
        },

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

            if (!this.form.first_name.trim()) {
                this.errors.first_name = "Це поле обов'язкове";
            } else if (/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/.test(this.form.first_name)) {
                this.errors.first_name = "Ім'я може містити лише букви";
            }

            if (!this.form.last_name.trim()) {
                this.errors.last_name = "Це поле обов'язкове";
            } else if (/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/.test(this.form.last_name)) {
                this.errors.last_name = "Прізвище може містити лише букви";
            }

            if (!this.form.phone_number.trim()) {
                this.errors.phone_number = "Це поле обов'язкове";
            } else if (/[^0-9+]/.test(this.form.phone_number)) {
                this.errors.phone_number = 'Номер може містити лише цифри та +';
            } else if (!this.validatePhone(this.form.phone_number)) {
                this.errors.phone_number = 'Невірний формат номера. Приклад: +380931234567';
            }

            if (!this.form.email.trim()) {
                this.errors.email = "Це поле обов'язкове";
            } else if (/[^a-zA-Z0-9@.]/.test(this.form.email)) {
                this.errors.email = 'Email може містити лише англійські букви, цифри та @.';
            } else if ((this.form.email.match(/@/g) || []).length !== 1) {
                this.errors.email = 'Email повинен містити один символ @';
            } else if (!this.validateEmail(this.form.email)) {
                this.errors.email = 'Невірний формат email';
            }

            if (this.showDeliveryAddress && !this.form.delivery_address.trim()) {
                this.errors.delivery_address = "Вкажіть адресу доставки";
            }

            if (this.items.length === 0) {
                this.errors.cart = 'Ваш кошик порожній';
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
            // Allow only letters (Ukrainian, English) and spaces, hyphens, apostrophes
            const filtered = event.target.value.replace(/[^a-zA-Zа-яА-ЯіІїЇєЄґҐ\s'\-]/g, '');
            this.form[field] = filtered;
            event.target.value = filtered;
            this.clearFieldError(field);
        },

        filterPhone(event) {
            // Allow only digits and + sign
            const filtered = event.target.value.replace(/[^0-9+]/g, '');
            this.form.phone_number = filtered;
            event.target.value = filtered;
            this.clearFieldError('phone_number');
        },

        filterEmail(event) {
            // Allow only English letters, digits, @, dot
            const filtered = event.target.value.replace(/[^a-zA-Z0-9@.]/g, '');
            this.form.email = filtered;
            event.target.value = filtered;
            this.clearFieldError('email');
        },

        // Cart item management methods
        async increaseQuantity(item) {
            if (item.quantity >= item.max_quantity) return;
            const newQuantity = item.quantity + 1;
            await this.updateQuantity(item, newQuantity);
        },

        async decreaseQuantity(item) {
            if (item.quantity > 1) {
                const newQuantity = item.quantity - 1;
                await this.updateQuantity(item, newQuantity);
            }
        },

        onQuantityInput(item, event) {
            const newQuantity = parseInt(event.target.value);

            if (newQuantity > item.max_quantity) {
                event.target.value = item.max_quantity;
                item.quantity = item.max_quantity;
                item._exceededMax = true;
                CartHandler.showNotification(
                    `На складі залишилось лише ${item.max_quantity} шт.`,
                    'warning'
                );
            } else if (newQuantity < 1 || isNaN(newQuantity)) {
                event.target.value = 1;
                item.quantity = 1;
                item._exceededMax = false;
            } else {
                item.quantity = newQuantity;
                item._exceededMax = false;
            }
        },

        async onQuantityChange(item, event) {
            const quantity = item.quantity;
            const skipMessage = item._exceededMax;
            item._exceededMax = false;
            await this.updateQuantity(item, quantity, skipMessage);
        },

        async updateQuantity(item, quantity, skipMessage = false) {
            const result = await CartHandler.changeQuantity(item.id, quantity);
            if (result && !result.error) {
                item.quantity = result.quantity || quantity;
                item.products_price = parseFloat((item.product_sell_price * item.quantity).toFixed(2));
                item.products_price_usd = parseFloat((item.product_price_usd * item.quantity).toFixed(2));
                this.recalculateTotals();
                if (!skipMessage) {
                    CartHandler.showNotification(result.message || 'Кількість змінено', 'success');
                }
            } else if (result && result.max_quantity) {
                item.max_quantity = result.max_quantity;
            }
        },

        async removeItem(item) {
            const result = await CartHandler.removeFromCart(item.id);
            if (result) {
                const index = this.items.findIndex(i => i.id === item.id);
                if (index > -1) {
                    this.items.splice(index, 1);
                }
                this.recalculateTotals();

                // Redirect to catalog if cart is empty
                if (this.items.length === 0) {
                    window.location.href = '/api/v1/catalog/all/';
                }
            }
        },

        recalculateTotals() {
            this.totalPrice = parseFloat(
                this.items.reduce((sum, item) => sum + item.products_price, 0).toFixed(2)
            );
            this.totalPriceUsd = parseFloat(
                this.items.reduce((sum, item) => sum + item.products_price_usd, 0).toFixed(2)
            );
            this.totalQuantity = this.items.reduce((sum, item) => sum + item.quantity, 0);
        },

        async submitOrder() {
            if (!this.validateForm()) {
                return;
            }

            this.isSubmitting = true;
            this.submitError = null;

            try {
                const response = await fetch('/api/v1/orders/create-order/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-CSRFToken': CartHandler.getCSRFToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        first_name: this.form.first_name,
                        last_name: this.form.last_name,
                        phone_number: this.form.phone_number,
                        email: this.form.email,
                        requires_delivery: this.form.requires_delivery === '1',
                        delivery_address: this.form.delivery_address,
                        payment_on_get: this.form.payment_on_get === '1'
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Помилка при створенні замовлення');
                }

                this.submitSuccess = true;
                CartHandler.showNotification('Замовлення успішно створено!', 'success');

                // Redirect to profile after success
                setTimeout(() => {
                    window.location.href = '/api/v1/users/orders/';
                }, 1500);
            } catch (error) {
                console.error('Error submitting order:', error);
                this.submitError = error.message || 'Помилка при створенні замовлення';
                CartHandler.showNotification(this.submitError, 'error');
            } finally {
                this.isSubmitting = false;
            }
        }
    },
    mounted() {
        this.fetchCart();

        // Pre-fill user data from data attributes
        const appElement = document.getElementById('order-app');
        if (appElement && appElement.dataset) {
            const userData = appElement.dataset;
            if (userData.firstName) this.form.first_name = userData.firstName;
            if (userData.lastName) this.form.last_name = userData.lastName;
            if (userData.email) this.form.email = userData.email;
        }
    }
}).mount('#order-app');
