const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            product: null,
            loading: true,
            currentImage: null,
            isFavorite: false,
            quantity: 1,
            productSlug: window.PRODUCT_CONFIG?.productSlug || ''
        }
    },
    computed: {
        maxQuantity() {
            if (!this.product) return 1;
            if (this.product.availability_status === 'last_item') {
                return Math.min(5, this.product.quantity);
            }
            if (this.product.availability_status === 'out_of_stock') {
                return 0;
            }
            return this.product.quantity;
        }
    },
    watch: {
        quantity(newVal, oldVal) {
            if (!this.product) return;

            // Перевірка на перевищення максимуму
            if (newVal > this.maxQuantity) {
                this.quantity = this.maxQuantity;
                CartHandler.showNotification(
                    `На складі залишилось лише ${this.maxQuantity} шт.`,
                    'warning'
                );
                return;
            }

            // Перевірка на мінімум
            if (newVal < 1) {
                this.quantity = 1;
            }
        }
    },
    methods: {
        async fetchProduct() {
            this.loading = true;
            try {
                const response = await fetch(`/api/v1/catalog/product/${this.productSlug}/`, {
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                if (!response.ok) throw new Error('Product not found');
                const data = await response.json();
                this.product = data.product;
                this.currentImage = this.product.image;
                document.title = this.product.name;
            } catch (error) {
                console.error('Error fetching product:', error);
                this.product = null;
            } finally {
                this.loading = false;
            }
        },
        setCurrentImage(image) {
            this.currentImage = image;
        },
        async toggleFavorite() {
            const result = await FavoritesHandler.toggleFavorite(this.product.id);
            if (result && !result.error) {
                this.isFavorite = result.is_favorited;
            }
        },
        async addToCart() {
            await CartHandler.addToCart(this.product.id, this.quantity);
        },
        formatId(id) {
            return String(id).padStart(4, '0');
        },
        getImages() {
            // Return array of 4 images (with placeholders if needed)
            const images = this.product.images || [];
            const result = [];
            for (let i = 0; i < 4; i++) {
                result.push(images[i] || { image: null, order: i });
            }
            return result;
        },
        increaseQuantity() {
            if (this.quantity < this.maxQuantity) {
                this.quantity++;
            }
        },
        decreaseQuantity() {
            if (this.quantity > 1) {
                this.quantity--;
            }
        }
    },
    async mounted() {
        await this.fetchProduct();
        // Перевірити чи товар в обраному
        await FavoritesHandler.init();
        if (this.product) {
            this.isFavorite = FavoritesHandler.isFavorite(this.product.id);
        }
    }
}).mount('#product-app');
