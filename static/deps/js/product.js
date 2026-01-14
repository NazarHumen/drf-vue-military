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
        toggleFavorite() {
            this.isFavorite = !this.isFavorite;
            // TODO: Implement favorites API
            console.log('Toggle favorite:', this.product.id);
        },
        addToCart() {
            // TODO: Implement cart API
            console.log('Add to cart:', this.product.id, 'quantity:', this.quantity);
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
            if (this.quantity < this.product.quantity) {
                this.quantity++;
            }
        },
        decreaseQuantity() {
            if (this.quantity > 1) {
                this.quantity--;
            }
        }
    },
    mounted() {
        this.fetchProduct();
    }
}).mount('#product-app');
