const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            items: [],
            totalCount: 0,
            loading: true,
            currentPage: 1,
            itemsPerPage: 8
        }
    },
    computed: {
        totalPages() {
            return Math.ceil(this.items.length / this.itemsPerPage);
        },
        paginatedItems() {
            const start = (this.currentPage - 1) * this.itemsPerPage;
            const end = start + this.itemsPerPage;
            return this.items.slice(start, end);
        },
        visiblePages() {
            const pages = [];
            const start = Math.max(1, this.currentPage - 2);
            const end = Math.min(this.totalPages, this.currentPage + 2);
            for (let i = start; i <= end; i++) {
                pages.push(i);
            }
            return pages;
        }
    },
    methods: {
        async fetchFavorites() {
            this.loading = true;
            try {
                const data = await FavoritesHandler.getFavorites();
                if (data) {
                    this.items = data.items || [];
                    this.totalCount = data.total_count || 0;
                    // Оновити бейдж у хедері
                    FavoritesHandler.updateFavoritesCount(this.totalCount);
                }
            } catch (error) {
                console.error('Error fetching favorites:', error);
            } finally {
                this.loading = false;
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
                    this.totalCount = this.items.length;
                    // Якщо на поточній сторінці більше немає товарів, перейти на попередню
                    if (this.paginatedItems.length === 0 && this.currentPage > 1) {
                        this.currentPage--;
                    }
                }
            }
        },

        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },

        async addToCart(productId) {
            await CartHandler.addToCart(productId);
        },

        formatId(id) {
            return String(id).padStart(4, '0');
        },

        truncate(text, length) {
            if (!text) return '';
            return text.length > length ? text.substring(0, length) + '...' : text;
        }
    },
    mounted() {
        this.fetchFavorites();

        // Оновлювати список при поверненні на сторінку (back/forward navigation)
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                this.fetchFavorites();
            }
        });

        // Оновлювати при поверненні на вкладку
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.fetchFavorites();
            }
        });
    }
}).mount('#favorites-app');
