/**
 * User Cart Vue App
 * Handles cart display and management (same style as order page)
 */
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            // Cart data
            cartItems: [],
            cartTotalPrice: 0,
            cartTotalPriceUsd: 0,
            cartTotalQuantity: 0,

            // UI state
            isLoading: true,
            error: null
        }
    },
    methods: {
        async fetchCart() {
            this.isLoading = true;
            this.error = null;

            try {
                const data = await CartHandler.getCart();
                if (data) {
                    this.cartItems = (data.items || []).map(item => ({
                        ...item,
                        updating: false,
                        removing: false,
                        _exceededMax: false
                    }));
                    this.cartTotalPrice = data.total_price || 0;
                    this.cartTotalPriceUsd = data.total_price_usd || 0;
                    this.cartTotalQuantity = data.total_quantity || 0;
                }
            } catch (error) {
                console.error('Cart fetch error:', error);
                this.error = 'Помилка завантаження кошика';
            } finally {
                this.isLoading = false;
            }
        },

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
                const index = this.cartItems.findIndex(i => i.id === item.id);
                if (index > -1) {
                    this.cartItems.splice(index, 1);
                }
                this.recalculateTotals();
            }
        },

        recalculateTotals() {
            this.cartTotalPrice = parseFloat(
                this.cartItems.reduce((sum, item) => sum + item.products_price, 0).toFixed(2)
            );
            this.cartTotalPriceUsd = parseFloat(
                this.cartItems.reduce((sum, item) => sum + item.products_price_usd, 0).toFixed(2)
            );
            this.cartTotalQuantity = this.cartItems.reduce((sum, item) => sum + item.quantity, 0);
        }
    },
    mounted() {
        this.fetchCart();
    }
}).mount('#user-cart-app');
