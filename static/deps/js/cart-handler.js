/**
 * CartHandler - глобальний модуль для роботи з кошиком
 * Використовується на сторінках catalog, product та basket
 */
const CartHandler = {
    /**
     * Додати товар до кошика
     * @param {number} productId - ID товару
     * @param {number} quantity - кількість (за замовчуванням 1)
     * @returns {Promise<Object>} - відповідь від API
     */
    async addToCart(productId, quantity = 1) {
        try {
            const response = await fetch('/api/v1/cart/cart_add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ product_id: productId, quantity: quantity })
            });

            const data = await response.json();

            if (response.ok) {
                this.updateCartCount();
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.error || 'Помилка додавання', 'error');
            }

            return data;
        } catch (error) {
            console.error('Cart error:', error);
            this.showNotification('Помилка з\'єднання', 'error');
            return null;
        }
    },

    /**
     * Змінити кількість товару в кошику
     * @param {number} cartId - ID елемента кошика
     * @param {number} quantity - нова кількість
     * @returns {Promise<Object>} - відповідь від API
     */
    async changeQuantity(cartId, quantity) {
        try {
            const response = await fetch('/api/v1/cart/cart_change/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ cart_id: cartId, quantity: quantity })
            });

            const data = await response.json();

            if (response.ok) {
                this.updateCartCount();
            } else {
                this.showNotification(data.error || 'Помилка зміни', 'error');
            }

            return data;
        } catch (error) {
            console.error('Cart error:', error);
            this.showNotification('Помилка з\'єднання', 'error');
            return null;
        }
    },

    /**
     * Видалити товар з кошика
     * @param {number} cartId - ID елемента кошика
     * @returns {Promise<Object>} - відповідь від API
     */
    async removeFromCart(cartId) {
        try {
            const response = await fetch('/api/v1/cart/cart_remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ cart_id: cartId })
            });

            const data = await response.json();

            if (response.ok) {
                this.updateCartCount();
                this.showNotification(data.message, 'remove');
            } else {
                this.showNotification(data.error || 'Помилка видалення', 'error');
            }

            return data;
        } catch (error) {
            console.error('Cart error:', error);
            this.showNotification('Помилка з\'єднання', 'error');
            return null;
        }
    },

    /**
     * Отримати список товарів у кошику
     * @returns {Promise<Object>} - дані кошика
     */
    async getCart() {
        try {
            const response = await fetch('/api/v1/cart/cart_list/', {
                headers: { 'Accept': 'application/json' }
            });
            return await response.json();
        } catch (error) {
            console.error('Cart fetch error:', error);
            return null;
        }
    },

    /**
     * Отримати CSRF token з cookies або DOM
     * @returns {string} - CSRF token
     */
    getCSRFToken() {
        // Спробувати отримати з DOM (якщо є форма з токеном)
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            return tokenElement.value;
        }

        // Отримати з cookies
        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieMatch) {
            return cookieMatch[1];
        }

        return '';
    },

    /**
     * Оновити лічильник товарів в хедері
     */
    async updateCartCount() {
        try {
            const data = await this.getCart();
            if (data) {
                const badge = document.getElementById('cart-count');
                if (badge) {
                    const count = data.total_quantity || 0;
                    badge.textContent = count;
                }
            }
        } catch (error) {
            console.error('Update cart count error:', error);
        }
    },

    /**
     * Показати iziToast notification
     * @param {string} message - текст повідомлення
     * @param {string} type - тип: 'success', 'error', 'warning', 'info'
     */
    showNotification(message, type = 'success') {
        if (typeof iziToast === 'undefined') {
            console.log(`[${type}] ${message}`);
            return;
        }

        const config = {
            message: `<strong>${message}</strong>`,
            position: 'topRight',
            timeout: 3000,
            progressBar: true,
            transitionIn: 'fadeInDown',
            transitionOut: 'fadeOutUp'
        };

        switch (type) {
            case 'success':
                iziToast.success({
                    ...config,
                    color: '#8B9A46',
                    icon: 'bx bx-check-circle'
                });
                break;
            case 'error':
                iziToast.error({
                    ...config,
                    icon: 'bx bx-x-circle'
                });
                break;
            case 'warning':
                iziToast.warning({
                    ...config,
                    icon: 'bx bx-error'
                });
                break;
            case 'info':
                iziToast.info({
                    ...config,
                    icon: 'bx bx-info-circle'
                });
                break;
            case 'remove':
                iziToast.show({
                    ...config,
                    color: '#2a2a2a',
                    icon: 'bx bx-trash',
                    iconColor: '#e74c3c',
                    messageColor: '#ffffff',
                    theme: 'dark'
                });
                break;
        }
    }
};

// Ініціалізувати лічильник при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    CartHandler.updateCartCount();
});
