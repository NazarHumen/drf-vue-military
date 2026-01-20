const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            products: [],
            categories: [],
            loading: true,
            searchQuery: '',
            sortBy: 'default',
            selectedCategories: [],
            currentPage: 1,
            totalPages: 1,
            totalCount: 0,
            searchTimeout: null,
            // Фільтр ціни
            priceRange: { min: 0, max: 10000 },
            priceMin: 0,
            priceMax: 10000,
            priceFilterActive: false,
            filteredCount: 0,
            // Категорії - показати ще
            showAllCategories: false,
            categoriesLimit: 7
        }
    },
    computed: {
        visibleCategories() {
            if (this.showAllCategories) {
                return this.categories;
            }
            return this.categories.slice(0, this.categoriesLimit);
        },
        hasMoreCategories() {
            return this.categories.length > this.categoriesLimit;
        },
        hiddenCategoriesCount() {
            return this.categories.length - this.categoriesLimit;
        },
        visiblePages() {
            const pages = [];
            const start = Math.max(1, this.currentPage - 2);
            const end = Math.min(this.totalPages, this.currentPage + 2);
            for (let i = start; i <= end; i++) {
                pages.push(i);
            }
            return pages;
        },
        allSelected() {
            return this.selectedCategories.length === 0;
        },
        totalProductsCount() {
            return this.categories.reduce((sum, cat) => sum + (cat.products_count || 0), 0);
        },
        sliderMinPercent() {
            const range = this.priceRange.max - this.priceRange.min;
            if (range === 0) return 0;
            return ((this.priceMin - this.priceRange.min) / range) * 100;
        },
        sliderMaxPercent() {
            const range = this.priceRange.max - this.priceRange.min;
            if (range === 0) return 100;
            return ((this.priceMax - this.priceRange.min) / range) * 100;
        }
    },
    methods: {
        async fetchCategories() {
            try {
                const response = await fetch('/api/v1/catalog/categories/', {
                    headers: { 'Accept': 'application/json' }
                });
                this.categories = await response.json();
            } catch (error) {
                console.error('Error fetching categories:', error);
            }
        },
        async fetchProducts(updatePriceRange = false) {
            this.loading = true;
            try {
                let url = '/api/v1/catalog/all/';
                const params = new URLSearchParams();

                if (this.searchQuery) {
                    url = '/api/v1/catalog/search/';
                    params.append('q', this.searchQuery);
                }

                // Множинний вибір категорій
                if (this.selectedCategories.length > 0) {
                    params.append('categories', this.selectedCategories.join(','));
                }

                // Фільтр ціни (тільки якщо активний)
                if (this.priceFilterActive) {
                    params.append('min_price', this.priceMin);
                    params.append('max_price', this.priceMax);
                }

                if (this.sortBy === 'on_sale') {
                    params.append('on_sale', 'true');
                } else if (this.sortBy !== 'default') {
                    params.append('order_by', this.sortBy);
                }
                if (this.currentPage > 1) {
                    params.append('page', this.currentPage);
                }

                const queryString = params.toString();
                if (queryString) {
                    url += '?' + queryString;
                }

                const response = await fetch(url, {
                    headers: { 'Accept': 'application/json' }
                });
                const data = await response.json();

                this.products = data.results || [];
                this.totalCount = data.total_items || 0;
                this.totalPages = data.total_pages || 1;
                this.filteredCount = data.total_items || 0;

                // Оновлюємо діапазон цін тільки при першому завантаженні
                if (updatePriceRange && data.price_range) {
                    this.priceRange.min = Math.floor(data.price_range.min);
                    this.priceRange.max = Math.ceil(data.price_range.max);
                    this.priceMin = this.priceRange.min;
                    this.priceMax = this.priceRange.max;
                }
            } catch (error) {
                console.error('Error fetching products:', error);
                this.products = [];
            } finally {
                this.loading = false;
            }
        },
        toggleCategory(slug) {
            const index = this.selectedCategories.indexOf(slug);
            if (index === -1) {
                this.selectedCategories.push(slug);
            } else {
                this.selectedCategories.splice(index, 1);
            }
            this.currentPage = 1;
            this.fetchProducts();
            this.updateUrl();
        },
        selectAll() {
            this.selectedCategories = [];
            this.currentPage = 1;
            this.fetchProducts();
            this.updateUrl();
        },
        isCategorySelected(slug) {
            return this.selectedCategories.includes(slug);
        },
        toggleShowAllCategories() {
            this.showAllCategories = !this.showAllCategories;
        },
        updateUrl() {
            let newUrl = '/api/v1/catalog/all/';
            const params = new URLSearchParams();

            if (this.selectedCategories.length > 0) {
                params.append('categories', this.selectedCategories.join(','));
            }
            if (this.priceFilterActive) {
                params.append('min_price', this.priceMin);
                params.append('max_price', this.priceMax);
            }

            const queryString = params.toString();
            if (queryString) {
                newUrl += '?' + queryString;
            }
            window.history.pushState({}, '', newUrl);
        },
        debouncedSearch() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.currentPage = 1;
                this.fetchProducts();
            }, 300);
        },
        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
                this.fetchProducts();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },
        toggleFavorite(productId) {
            // TODO: Implement favorites API
            console.log('Toggle favorite:', productId);
        },
        async addToCart(productId) {
            await CartHandler.addToCart(productId);
        },
        truncate(text, length) {
            if (!text) return '';
            return text.length > length ? text.substring(0, length) + '...' : text;
        },
        formatId(id) {
            return String(id).padStart(4, '0');
        },
        // Методи для цінового фільтра
        onPriceMinInput(event) {
            let value = parseInt(event.target.value) || this.priceRange.min;
            if (value < this.priceRange.min) value = this.priceRange.min;
            if (value > this.priceMax - 1) value = this.priceMax - 1;
            this.priceMin = value;
        },
        onPriceMaxInput(event) {
            let value = parseInt(event.target.value) || this.priceRange.max;
            if (value > this.priceRange.max) value = this.priceRange.max;
            if (value < this.priceMin + 1) value = this.priceMin + 1;
            this.priceMax = value;
        },
        onSliderMinInput(event) {
            let value = parseInt(event.target.value);
            if (value > this.priceMax - 1) value = this.priceMax - 1;
            this.priceMin = value;
        },
        onSliderMaxInput(event) {
            let value = parseInt(event.target.value);
            if (value < this.priceMin + 1) value = this.priceMin + 1;
            this.priceMax = value;
        },
        applyPriceFilter() {
            this.priceFilterActive = true;
            this.currentPage = 1;
            this.fetchProducts();
            this.updateUrl();
        },
        clearPriceFilter() {
            this.priceFilterActive = false;
            this.priceMin = this.priceRange.min;
            this.priceMax = this.priceRange.max;
            this.currentPage = 1;
            this.fetchProducts();
            this.updateUrl();
        }
    },
    mounted() {
        // Завантажити параметри з URL якщо є
        const urlParams = new URLSearchParams(window.location.search);
        const categoriesParam = urlParams.get('categories');
        if (categoriesParam) {
            this.selectedCategories = categoriesParam.split(',').filter(s => s);
        }

        const minPriceParam = urlParams.get('min_price');
        const maxPriceParam = urlParams.get('max_price');
        if (minPriceParam || maxPriceParam) {
            this.priceFilterActive = true;
            if (minPriceParam) this.priceMin = parseInt(minPriceParam);
            if (maxPriceParam) this.priceMax = parseInt(maxPriceParam);
        }

        this.fetchCategories();
        this.fetchProducts(true); // true = оновити діапазон цін
    }
}).mount('#catalog-app');
