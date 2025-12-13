// Когда html документ готов (прорисован)
$(document).ready(function () {
    // берем в переменную элемент разметки с id jq-notification для оповещений от ajax
    var successMessage = $("#jq-notification");

    // Ловим собыитие клика по кнопке добавить в корзину
    $(document).on("click", ".add-to-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $("#goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.text() || 0);

        // Получаем id товара из атрибута data-product-id
        var product_id = $(this).data("product-id");

        // Из атрибута href берем ссылку на контроллер django
        var add_to_cart_url = $(this).attr("href");

        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({
            type: "POST",
            url: add_to_cart_url,
            data: {
                product_id: product_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);


                // Увеличиваем количество товаров в корзине (отрисовка в шаблоне)
                cartCount++;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },

            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    });

    // Ловим собыитие клика по кнопке удалить товар из корзины
    $(document).on("click", ".remove-from-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $("#goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.text() || 0);

        // Получаем id корзины из атрибута data-cart-id
        var cart_id = $(this).data("cart-id");
        // Из атрибута href берем ссылку на контроллер django
        var remove_from_cart = $(this).attr("href");

        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({

            type: "POST",
            url: remove_from_cart,
            data: {
                cart_id: cart_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);

                // Уменьшаем количество товаров в корзине (отрисовка)
                cartCount -= data.quantity_deleted;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },

            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    });


    // Теперь + - количества товара
    // Обработчик события для уменьшения значения
    $(document).on("click", ".decrement", function () {
        // Берем ссылку на контроллер django из атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Берем id корзины из атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Ищем ближайшеий input с количеством
        var $input = $(this).closest('.input-group').find('.number');
        // Берем значение количества товара
        var currentValue = parseInt($input.val());
        // Если количества больше одного, то только тогда делаем -1
        if (currentValue > 1) {
            $input.val(currentValue - 1);
            // Запускаем функцию определенную ниже
            // с аргументами (id карты, новое количество, количество уменьшилось или прибавилось, url)
            updateCart(cartID, currentValue - 1, -1, url);
        }
    });

    // Обработчик события для увеличения значения
    $(document).on("click", ".increment", function () {
        // Берем ссылку на контроллер django из атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Берем id корзины из атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Ищем ближайшеий input с количеством
        var $input = $(this).closest('.input-group').find('.number');
        // Берем значение количества товара
        var currentValue = parseInt($input.val());

        $input.val(currentValue + 1);

        // Запускаем функцию определенную ниже
        // с аргументами (id карты, новое количество, количество уменьшилось или прибавилось, url)
        updateCart(cartID, currentValue + 1, 1, url);
    });

    function updateCart(cartID, quantity, change, url) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                cart_id: cartID,
                quantity: quantity,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },

            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 7сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 7000);

                // Изменяем количество товаров в корзине
                var goodsInCartCount = $("#goods-in-cart-count");
                var cartCount = parseInt(goodsInCartCount.text() || 0);
                cartCount += change;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },
            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    }


    // Берем из разметки элемент по id - оповещения от django
    var notification = $('#notification');
    // И через 7 сек. убираем
    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');
        }, 7000);
    }

    // При клике по значку корзины открываем всплывающее(модальное) окно
    $('#modalButton').click(function () {
        $('#exampleModal').appendTo('body');

        $('#exampleModal').modal('show');
    });

    // Собыите клик по кнопке закрыть окна корзины
    $('#exampleModal .btn-close').click(function () {
        $('#exampleModal').modal('hide');
    });


    // Обработчик события радиокнопки выбора способа доставки
    $("input[name='requires_delivery']").change(function () {
        var selectedValue = $(this).val();
        // Скрываем или отображаем input ввода адреса доставки
        if (selectedValue === "1") {
            $("#deliveryAddressField").show();
        } else {
            $("#deliveryAddressField").hide();
        }
    });
});


//close-button

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.close-button').forEach(button => {
        button.addEventListener('click', function () {
            // window.history.back(); // Повертає користувача на попередню сторінку

            if (document.referrer) {
                window.location.href = document.referrer;
            } else {
                window.history.back();
            }
        });

    });
});

// // Форматування введення номера телефону у формі (xxx) xxx-хххx
//    document.getElementById('id_phone_number').addEventListener('input', function (e) {
//        var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
//        e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
//    });
// // Перевіряємо на стороні клієнта коректність номера телефону у формі xxx-xxx-хх-хx
//    $('#create_order_form').on('submit', function (event) {
//        var phoneNumber = $('#id_phone_number').val();
//        var regex = /^\(\d{3}\) \d{3}-\d{4}$/;
//        if (!regex.test(phoneNumber)) {
//            $('#phone_number_error').show();
//            event.preventDefault();
//        } else {
//            $('#phone_number_error').hide();
//           // Очищення номера телефону від дужок та тире перед відправкою форми
//            var cleanedPhoneNumber = phoneNumber.replace(/[()\-\s]/g, '');
//            $('#id_phone_number').val(cleanedPhoneNumber);
//        }
//    });

// // Форматування введення номера телефону у формі (xxx) xxx-хххx
// $('#id_phone_number').on('input', function (e) {
//     var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
//     e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
// });
//
// // Перевіряємо на стороні клієнта коректність номера телефону у формі (xxx) xxx-xxxx
// $('#create_order_form').on('submit', function (event) {
//     var phoneNumber = $('#id_phone_number').val();
//     var regex = /^\(\d{3}\) \d{3}-\d{4}$/;
//     if (!regex.test(phoneNumber)) {
//         $('#phone_number_error').show();
//         event.preventDefault();
//     } else {
//         $('#phone_number_error').hide();
//         // Очищення номера телефону від дужок та тире перед відправкою форми
//         var cleanedPhoneNumber = phoneNumber.replace(/[()\-\s]/g, '');
//         $('#id_phone_number').val(cleanedPhoneNumber);
//     }
// });


// Валідація номера телефону помилка консоль

// document.addEventListener("DOMContentLoaded", function () {
//     const phoneInput = document.getElementById("id_phone_number");
//     const errorDiv = document.getElementById("phone_number_error");
//
//     phoneInput.addEventListener("input", function () {
//         let value = phoneInput.value;
//
//         // 🔐 Видалити всі символи, крім цифр і +
//         value = value.replace(/[^\d+]/g, '');
//
//         // ❗ Залишити тільки один плюс на початку
//         if (value.indexOf('+') > 0) {
//             value = value.replace(/\+/g, '');
//             value = '+' + value;
//         } else if (value.indexOf('+') === -1) {
//             value = '+' + value;
//         }
//
//         // 📏 Обмежити кількість символів залежно від коду країни
//         if (value.startsWith('+380')) {
//             value = value.slice(0, 13); // +380XXXXXXXXX → 13 символів
//         } else if (value.startsWith('+46')) {
//             value = value.slice(0, 12); // +46XXXXXXXXX → до 12 символів
//         } else {
//             value = value.slice(0, 16); // На випадок інших кодів
//         }
//
//         phoneInput.value = value;
//
//         // 🔍 Перевірка валідності
//         errorDiv.style.display = isValidPhone(value) ? "none" : "block";
//     });
//
//     function isValidPhone(value) {
//         return /^(\+380\d{9}|\+46\d{7,10})$/.test(value);
//     }
//
//     phoneInput.form.addEventListener("submit", function (e) {
//         const value = phoneInput.value.trim();
//         if (!isValidPhone(value)) {
//             e.preventDefault();
//             errorDiv.style.display = "block";
//         }
//     });
// });
//
//
//
// document.addEventListener("DOMContentLoaded", function () {
//     const phoneInput = document.getElementById("id_phone");
//     const errorDiv = document.getElementById("phone_error");
//
//     phoneInput.addEventListener("input", function () {
//         let value = phoneInput.value;
//
//         // Видалити всі символи, крім цифр і +
//         value = value.replace(/[^\d+]/g, '');
//
//         // Залишити тільки один плюс на початку
//         if (value.indexOf('+') > 0) {
//             value = value.replace(/\+/g, '');
//             value = '+' + value;
//         } else if (value.indexOf('+') === -1) {
//             value = '+' + value;
//         }
//
//         // Обмежити довжину залежно від коду країни
//         if (value.startsWith('+380')) {
//             value = value.slice(0, 13); // +380XXXXXXXXX → 13 символів
//         } else if (value.startsWith('+46')) {
//             value = value.slice(0, 12); // +46XXXXXXXXX → до 12 символів
//         } else {
//             value = value.slice(0, 16); // На випадок інших кодів
//         }
//
//         phoneInput.value = value;
//
//         // Показати/сховати помилку
//         errorDiv.style.display = isValidPhone(value) ? "none" : "block";
//     });
//
//     function isValidPhone(value) {
//         return /^(\+380\d{9}|\+46\d{7,10})$/.test(value);
//     }
//
//     phoneInput.form.addEventListener("submit", function (e) {
//         const value = phoneInput.value.trim();
//         if (!isValidPhone(value)) {
//             e.preventDefault();
//             errorDiv.style.display = "block";
//             phoneInput.focus();
//         }
//     });
// });


// Валідація номера телефону у формі правильно
document.addEventListener("DOMContentLoaded", function () {
    function setupPhoneValidation(inputId, errorId) {
        const phoneInput = document.getElementById(inputId);
        const errorDiv = document.getElementById(errorId);

        if (!phoneInput || !errorDiv) return;

        // ✨ Обробка вводу
        phoneInput.addEventListener("input", function () {
            let value = phoneInput.value;
            value = value.replace(/[^\d+]/g, '');

            if (value.indexOf('+') > 0) {
                value = value.replace(/\+/g, '');
                value = '+' + value;
            } else if (value.indexOf('+') === -1) {
                value = '+' + value;
            }

            if (value.startsWith('+380')) {
                value = value.slice(0, 13);
            } else if (value.startsWith('+46')) {
                value = value.slice(0, 12);
            } else {
                value = value.slice(0, 16);
            }

            phoneInput.value = value;
            errorDiv.style.display = isValidPhone(value) ? "none" : "block";
        });

        // ✨ Перевірка при сабміті форми
        phoneInput.form.addEventListener("submit", function (e) {
            const value = phoneInput.value.trim();
            if (!isValidPhone(value)) {
                e.preventDefault();
                errorDiv.style.display = "block";
                phoneInput.focus();
            }
        });
    }

    function isValidPhone(value) {
        return /^(\+380\d{9}|\+46\d{7,10})$/.test(value);
    }

    // 🧩 Викликаємо для кожної форми
    setupPhoneValidation("id_phone_number", "phone_number_error");
    setupPhoneValidation("id_phone", "phone_error");
});








//копіювання номера


//Виправлення офрмлення замовлення
document.querySelectorAll('.increment, .decrement').forEach(button => {
    button.addEventListener('click', function (event) {
        const cartId = this.dataset.cartId;
        const url = this.dataset.cartChangeUrl;
        const action = this.classList.contains('increment') ? 'increment' : 'decrement';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({cart_id: cartId, action: action})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Оновлення кількості
                    document.querySelector(`[data-cart-id="${cartId}"]`).closest('.list-group-item')
                        .querySelector('.number').value = data.quantity;

                    // Оновлення суми товарів
                    document.querySelector(`[data-cart-id="${cartId}"]`).closest('.list-group-item')
                        .querySelector('strong').textContent = `${data.products_price} $`;

                    // Оновлення загальної суми та кількості
                    document.querySelector('.card-footer .float-left strong').textContent = data.total_quantity;
                    document.querySelector('.card-footer h4 strong').textContent = `${data.total_price} $`;
                }
            })
            .catch(error => console.error('Error:', error));
    });
});





$(document).ready(function () {
    $('#languageSelect').change(function () {
        $('#languageForm').submit();  // Автоматично надсилає форму при зміні мови
    });
});







// favorites-modal













