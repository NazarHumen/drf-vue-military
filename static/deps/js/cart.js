const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            items: [],
            totalPrice: 0,
            totalPriceUsd: 0,
            totalQuantity: 0,
            loading: true
        }
    },
    methods: {
        async fetchCart() {
            this.loading = true;
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
            } finally {
                this.loading = false;
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
                // Оновлюємо локальний стан
                item.quantity = result.quantity || quantity;
                // Перераховуємо ціни для цього item
                item.products_price = parseFloat((item.product_sell_price * item.quantity).toFixed(2));
                item.products_price_usd = parseFloat((item.product_price_usd * item.quantity).toFixed(2));
                // Перераховуємо загальні суми
                this.recalculateTotals();
                // Показуємо повідомлення тільки якщо не було попередження про ліміт
                if (!skipMessage) {
                    CartHandler.showNotification(result.message || 'Кількість змінено', 'success');
                }
            } else if (result && result.max_quantity) {
                // Якщо є помилка з max_quantity, оновлюємо локальний ліміт
                item.max_quantity = result.max_quantity;
            }
        },

        async removeItem(item) {
            const result = await CartHandler.removeFromCart(item.id);
            if (result) {
                // Видаляємо item з локального масиву
                const index = this.items.findIndex(i => i.id === item.id);
                if (index > -1) {
                    this.items.splice(index, 1);
                }
                // Перераховуємо загальні суми
                this.recalculateTotals();
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

        formatId(id) {
            return String(id).padStart(4, '0');
        },

        truncate(text, length) {
            if (!text) return '';
            return text.length > length ? text.substring(0, length) + '...' : text;
        }
    },
    mounted() {
        this.fetchCart();
    }
}).mount('#cart-app');
