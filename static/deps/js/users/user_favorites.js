const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            items: [],
            isLoading: true,
            error: null
        }
    },
    methods: {
        async fetchFavorites() {
            this.isLoading = true;
            this.error = null;
            try {
                const data = await FavoritesHandler.getFavorites();
                if (data) {
                    this.items = data.items || [];
                    FavoritesHandler.updateFavoritesCount(data.total_count || 0);
                }
            } catch (error) {
                console.error('Error fetching favorites:', error);
                this.error = 'Помилка завантаження обраного';
            } finally {
                this.isLoading = false;
            }
        },

        async removeItem(item) {
            const result = await FavoritesHandler.removeFavorite(
                item.product_id,
                item.id
            );
            if (result && !result.error) {
                const index = this.items.findIndex(i => i.id === item.id);
                if (index > -1) {
                    this.items.splice(index, 1);
                }
            }
        },

        async addToCart(productId) {
            await CartHandler.addToCart(productId);
        },

        formatId(id) {
            return String(id).padStart(4, '0');
        }
    },
    mounted() {
        this.fetchFavorites();

        // Оновлювати при поверненні на сторінку
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                this.fetchFavorites();
            }
        });

        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.fetchFavorites();
            }
        });
    }
}).mount('#user-favorites-app');
