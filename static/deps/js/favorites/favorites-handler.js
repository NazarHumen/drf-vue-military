/**
 * FavoritesHandler - глобальний модуль для роботи з обраним
 * Використовується на сторінках catalog, product та favorites
 */
const FavoritesHandler = {
    // Кеш ID обраних товарів для швидкої перевірки
    _favoriteIds: new Set(),
    _initialized: false,

    /**
     * Ініціалізація - завантаження всіх ID обраних товарів у кеш
     * @returns {Promise<Set>} - set ID обраних товарів
     */
    async init() {
        if (this._initialized) return this._favoriteIds;
        try {
            const response = await fetch('/api/v1/favorites/check/', {
                headers: { 'Accept': 'application/json' }
            });
            const data = await response.json();
            this._favoriteIds = new Set(data.favorite_ids || []);
            this._initialized = true;
            this.updateFavoritesCount();
            return this._favoriteIds;
        } catch (error) {
            console.error('Favorites init error:', error);
            return this._favoriteIds;
        }
    },

    /**
     * Перевірити чи товар в обраному (з кешу)
     * @param {number} productId
     * @returns {boolean}
     */
    isFavorite(productId) {
        return this._favoriteIds.has(Number(productId));
    },

    /**
     * Отримати масив ID обраних товарів (з кешу)
     * @returns {Array<number>}
     */
    getFavoriteIds() {
        return Array.from(this._favoriteIds);
    },

    /**
     * Додати товар в обране
     * @param {number} productId
     * @returns {Promise<Object>}
     */
    async addFavorite(productId) {
        try {
            const response = await fetch('/api/v1/favorites/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ product_id: productId })
            });

            const data = await response.json();

            if (response.ok) {
                this._favoriteIds.add(Number(productId));
                this.updateFavoritesCount(data.total_count);
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.error || 'Помилка додавання', 'error');
            }

            return data;
        } catch (error) {
            console.error('Favorites error:', error);
            this.showNotification('Помилка з\'єднання', 'error');
            return null;
        }
    },

    /**
     * Видалити товар з обраного
     * @param {number} productId - ID товару
     * @param {number} favoriteId - ID запису обраного (опціонально)
     * @returns {Promise<Object>}
     */
    async removeFavorite(productId, favoriteId = null) {
        try {
            const body = favoriteId
                ? { favorite_id: favoriteId }
                : { product_id: productId };

            const response = await fetch('/api/v1/favorites/remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(body)
            });

            const data = await response.json();

            if (response.ok) {
                this._favoriteIds.delete(Number(productId));
                this.updateFavoritesCount(data.total_count);
                this.showNotification(data.message, 'remove');
            } else {
                this.showNotification(data.error || 'Помилка видалення', 'error');
            }

            return data;
        } catch (error) {
            console.error('Favorites error:', error);
            this.showNotification('Помилка з\'єднання', 'error');
            return null;
        }
    },

    /**
     * Перемкнути статус обраного
     * @param {number} productId
     * @returns {Promise<Object>}
     */
    async toggleFavorite(productId) {
        try {
            const response = await fetch('/api/v1/favorites/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ product_id: productId })
            });

            const data = await response.json();

            if (response.ok) {
                if (data.is_favorited) {
                    this._favoriteIds.add(Number(productId));
                } else {
                    this._favoriteIds.delete(Number(productId));
                }
                this.updateFavoritesCount(data.total_count);
                this.showNotification(data.message, data.is_favorited ? 'success' : 'remove');
            } else {
                this.showNotification(data.error || 'Помилка', 'error');
            }

            return data;
        } catch (error) {
            console.error('Favorites error:', error);
            this.showNotification('Помилка з\'єднання', 'error');
            return null;
        }
    },

    /**
     * Отримати повний список обраних товарів з деталями
     * @returns {Promise<Object>}
     */
    async getFavorites() {
        try {
            const response = await fetch('/api/v1/favorites/list/', {
                headers: { 'Accept': 'application/json' }
            });
            return await response.json();
        } catch (error) {
            console.error('Favorites fetch error:', error);
            return null;
        }
    },

    /**
     * Отримати CSRF token з cookies або DOM
     * @returns {string} - CSRF token
     */
    getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            return tokenElement.value;
        }

        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieMatch) {
            return cookieMatch[1];
        }

        return '';
    },

    /**
     * Оновити лічильник обраних у хедері
     * @param {number} count - кількість (опціонально)
     */
    updateFavoritesCount(count = null) {
        const badge = document.getElementById('favorites-count');
        if (badge) {
            const displayCount = count !== null ? count : this._favoriteIds.size;
            badge.textContent = displayCount;
        }
    },

    /**
     * Показати iziToast notification
     * @param {string} message - текст повідомлення
     * @param {string} type - тип: 'success', 'error', 'remove'
     */
    showNotification(message, type = 'success') {
        // Делегувати до CartHandler якщо доступний
        if (typeof CartHandler !== 'undefined' && CartHandler.showNotification) {
            CartHandler.showNotification(message, type);
            return;
        }

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
                    icon: 'bx bx-heart'
                });
                break;
            case 'error':
                iziToast.error({
                    ...config,
                    icon: 'bx bx-x-circle'
                });
                break;
            case 'remove':
                iziToast.show({
                    ...config,
                    color: '#2a2a2a',
                    icon: 'bx bx-heart',
                    iconColor: '#e74c3c',
                    messageColor: '#ffffff',
                    theme: 'dark'
                });
                break;
            default:
                iziToast.info({
                    ...config,
                    icon: 'bx bx-info-circle'
                });
        }
    }
};

// Ініціалізувати обране при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    FavoritesHandler.init();
});
