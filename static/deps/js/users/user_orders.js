/**
 * User Orders Vue App
 * Handles orders display
 */
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            // Orders data
            orders: [],
            activeOrderId: null,

            // UI state
            isLoading: true,
            error: null
        }
    },
    methods: {
        async fetchOrders() {
            this.isLoading = true;
            this.error = null;

            try {
                const response = await fetch('/api/v1/users/profile/', {
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin'
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.replace('/api/v1/users/login/?next=/api/v1/users/orders/');
                        return;
                    }
                    throw new Error('Помилка завантаження замовлень');
                }

                const data = await response.json();
                this.orders = data.orders || [];

                // Set first order as active
                if (this.orders.length > 0) {
                    this.activeOrderId = this.orders[0].id;
                }

            } catch (error) {
                console.error('Orders fetch error:', error);
                this.error = error.message;
            } finally {
                this.isLoading = false;
            }
        },

        toggleOrder(orderId) {
            this.activeOrderId = this.activeOrderId === orderId ? null : orderId;
        },

        isOrderActive(orderId) {
            return this.activeOrderId === orderId;
        },

        getOrderItemPrice(item) {
            return parseFloat((item.price * item.quantity).toFixed(2));
        },

        getOrderTotal(order) {
            if (!order.items) return 0;
            return parseFloat(
                order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)
            );
        },

        getOrderTotalUsd(order) {
            if (!order.items) return null;
            const total = order.items.reduce((sum, item) => {
                return sum + (item.products_price_usd || 0);
            }, 0);
            return total > 0 ? total : null;
        },

        // Format helpers
        formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('uk-UA', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        getStatusDisplay(status) {
            const statusMap = {
                'processing': 'В обробці',
                'shipped': 'Відправлено',
                'delivered': 'Доставлено'
            };
            return statusMap[status] || status;
        },

        getStatusClass(status) {
            const classes = {
                'processing': 'bg-warning text-dark',
                'shipped': 'bg-info',
                'delivered': 'bg-success'
            };
            return classes[status] || 'bg-secondary';
        }
    },
    mounted() {
        this.fetchOrders();
    }
}).mount('#user-orders-app');
