// Hero Carousel Vue App
document.addEventListener('DOMContentLoaded', function() {
    const { createApp } = Vue;

    createApp({
        delimiters: ['[[', ']]'],
        data() {
            return {
                currentSlide: 0,
                autoplayInterval: null,
                slides: window.HERO_SLIDES || []
            }
        },
        computed: {
            currentTitleFirst() {
                const words = this.slides[this.currentSlide]?.title.split(' ') || [];
                return words[0] || '';
            },
            currentTitleSecond() {
                const words = this.slides[this.currentSlide]?.title.split(' ') || [];
                return words.slice(1).join(' ') || '';
            },
            currentSubtitle() {
                return this.slides[this.currentSlide]?.subtitle || '';
            }
        },
        methods: {
            goToSlide(index) {
                this.currentSlide = index;
                this.resetAutoplay();
            },
            startAutoplay() {
                this.autoplayInterval = setInterval(() => {
                    this.currentSlide = (this.currentSlide + 1) % this.slides.length;
                }, 5000);
            },
            resetAutoplay() {
                clearInterval(this.autoplayInterval);
                this.startAutoplay();
            }
        },
        mounted() {
            this.startAutoplay();
        },
        beforeUnmount() {
            clearInterval(this.autoplayInterval);
        }
    }).mount('#hero-app');
});
