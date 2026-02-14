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
            cartQuantity: 0,
            suppressWatch: false,
            productSlug: window.PRODUCT_CONFIG?.productSlug || ''
        }
    },
    computed: {
        maxQuantity() {
            if (!this.product) return 1;
            let max;
            if (this.product.availability_status === 'last_item') {
                max = Math.min(5, this.product.quantity);
            } else if (this.product.availability_status === 'out_of_stock') {
                return 0;
            } else {
                max = this.product.quantity;
            }
            // Віднімаємо кількість, яка вже є в кошику
            return Math.max(0, max - this.cartQuantity);
        }
    },
    watch: {
        quantity(newVal, oldVal) {
            if (!this.product || this.suppressWatch) return;

            // Перевірка на перевищення максимуму
            if (newVal > this.maxQuantity) {
                this.quantity = this.maxQuantity;
                if (this.maxQuantity > 0) {
                    CartHandler.showNotification(
                        `Можна додати ще ${this.maxQuantity} шт.`,
                        'warning'
                    );
                }
                return;
            }

            // Перевірка на мінімум
            if (newVal < 1 && this.maxQuantity > 0) {
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
            const result = await CartHandler.addToCart(this.product.id, this.quantity);
            if (result && !result.error) {
                this.suppressWatch = true;
                this.cartQuantity += this.quantity;
                this.quantity = this.maxQuantity > 0 ? 1 : 0;
                this.$nextTick(() => { this.suppressWatch = false; });
            }
        },
        async fetchCartQuantity() {
            const data = await CartHandler.getCart();
            if (data && data.items) {
                const cartItem = data.items.find(item => item.product_id === this.product.id);
                this.cartQuantity = cartItem ? cartItem.quantity : 0;
            }
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
        if (this.product) {
            // Перевірити чи товар в обраному та кількість в кошику
            await Promise.all([
                FavoritesHandler.init(),
                this.fetchCartQuantity()
            ]);
            this.isFavorite = FavoritesHandler.isFavorite(this.product.id);
        }
    }
}).mount('#product-app');
