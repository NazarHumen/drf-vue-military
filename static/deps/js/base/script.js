const { createApp } = Vue;

createApp({
    data() {
        return {
            selected: "uk"
        }
    },
    mounted() {
        this.selected = this.getCookie("django_language") || "uk";
    },
    methods: {
        changeLang() {
            fetch("/i18n/setlang/", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": this.getCookie("csrftoken")
                },
                body: `language=${this.selected}&next=/`
            }).then(() => {
                window.location.reload();
            });
        },

        getCookie(name) {
            let cookieValue = null;
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
            return cookieValue;
        }
    }
}).mount("#app");
