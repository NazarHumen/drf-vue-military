from decimal import Decimal
from unittest.mock import Mock

from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.carts.mixins import CartMixin
from apps.carts.models import Cart
from apps.carts.utils import get_user_carts
from apps.goods.models import Categories, ExchangeRate, Products
from apps.users.models import User


class CartModelTestCase(TestCase):
    """Tests for Cart model"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for entire test class"""
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        """Set up test data for each test"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("1000.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
            availability_status="ready_to_ship",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )

    def test_cart_creation(self):
        """Test cart item is created correctly"""
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.product, self.product)
        self.assertEqual(self.cart.quantity, 2)

    def test_cart_str_with_user(self):
        """Test cart string representation with user"""
        expected = f"Кошик {self.user.username} | Товар {self.product.name} | Кількість 2"
        self.assertEqual(str(self.cart), expected)

    def test_cart_str_anonymous(self):
        """Test cart string representation for anonymous user"""
        cart = Cart.objects.create(
            user=None,
            session_key="test_session_key",
            product=self.product,
            quantity=1,
        )
        expected = f"Кошик Anonymous user | Товар {self.product.name} | Кількість 1"
        self.assertEqual(str(cart), expected)

    def test_products_price(self):
        """Test products_price calculates correctly"""
        expected_price = round(self.product.sell_price() * self.cart.quantity, 2)
        self.assertEqual(self.cart.products_price(), expected_price)

    def test_products_price_usd(self):
        """Test products_price_usd calculates correctly"""
        expected_price = round(self.product.price_in_usd * self.cart.quantity, 2)
        self.assertEqual(self.cart.products_price_usd(), expected_price)

    def test_cart_default_quantity(self):
        """Test cart default quantity is 0"""
        cart = Cart.objects.create(
            user=self.user,
            product=self.product,
        )
        self.assertEqual(cart.quantity, 0)

    def test_cart_ordering(self):
        """Test carts are ordered by id"""
        cart2 = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=1,
        )
        carts = list(Cart.objects.all())
        self.assertEqual(carts[0].id, self.cart.id)
        self.assertEqual(carts[1].id, cart2.id)


class CartQuerysetTestCase(TestCase):
    """Tests for CartQueryset methods"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product1 = Products.objects.create(
            name="Product 1",
            slug="product-1",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
        )
        self.product2 = Products.objects.create(
            name="Product 2",
            slug="product-2",
            price=Decimal("200.00"),
            quantity=5,
            category=self.category,
            currency="UAH",
        )
        self.cart1 = Cart.objects.create(
            user=self.user,
            product=self.product1,
            quantity=2,
        )
        self.cart2 = Cart.objects.create(
            user=self.user,
            product=self.product2,
            quantity=3,
        )

    def test_total_quantity(self):
        """Test total_quantity returns sum of all quantities"""
        carts = Cart.objects.filter(user=self.user)
        self.assertEqual(carts.total_quantity(), 5)

    def test_total_quantity_empty(self):
        """Test total_quantity returns 0 for empty queryset"""
        carts = Cart.objects.none()
        self.assertEqual(carts.total_quantity(), 0)

    def test_total_price(self):
        """Test total_price returns sum of all product prices"""
        carts = Cart.objects.filter(user=self.user)
        expected = self.cart1.products_price() + self.cart2.products_price()
        self.assertEqual(carts.total_price(), expected)

    def test_total_price_usd(self):
        """Test total_price_usd returns sum in USD"""
        carts = Cart.objects.filter(user=self.user)
        expected = self.cart1.products_price_usd() + self.cart2.products_price_usd()
        self.assertEqual(carts.total_price_usd(), expected)


class CartUtilsTestCase(TestCase):
    """Tests for cart utils functions"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )

    def test_get_user_carts_authenticated(self):
        """Test get_user_carts for authenticated user"""
        request = self.factory.get("/")
        request.user = self.user
        carts = get_user_carts(request)
        self.assertEqual(carts.count(), 1)
        self.assertEqual(carts.first(), self.cart)

    def test_get_user_carts_anonymous(self):
        """Test get_user_carts for anonymous user"""
        session_key = "test_session_key"
        Cart.objects.create(
            session_key=session_key,
            product=self.product,
            quantity=1,
        )

        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False
        request.session = Mock()
        request.session.session_key = session_key
        request.session.create = Mock()

        carts = get_user_carts(request)
        self.assertEqual(carts.count(), 1)

    def test_get_user_carts_creates_session(self):
        """Test get_user_carts creates session if not exists"""
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False
        request.session = Mock()
        request.session.session_key = None
        request.session.create = Mock()

        get_user_carts(request)
        request.session.create.assert_called_once()


class CartMixinTestCase(TestCase):
    """Tests for CartMixin"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.mixin = CartMixin()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
            availability_status="ready_to_ship",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )

    def _get_authenticated_request(self):
        request = self.factory.get("/")
        request.user = self.user
        request.session = Mock()
        request.session.session_key = None
        return request

    def _get_anonymous_request(self, session_key="test_session"):
        request = self.factory.get("/")
        request.user = Mock()
        request.user.is_authenticated = False
        request.session = Mock()
        request.session.session_key = session_key
        request.session.create = Mock()
        return request

    def test_get_cart_by_product(self):
        """Test get_cart returns cart by product"""
        request = self._get_authenticated_request()
        cart = self.mixin.get_cart(request, product=self.product)
        self.assertEqual(cart, self.cart)

    def test_get_cart_by_id(self):
        """Test get_cart returns cart by id"""
        request = self._get_authenticated_request()
        cart = self.mixin.get_cart(request, cart_id=self.cart.id)
        self.assertEqual(cart, self.cart)

    def test_get_cart_anonymous(self):
        """Test get_cart for anonymous user"""
        session_key = "anon_session"
        anon_cart = Cart.objects.create(
            session_key=session_key,
            product=self.product,
            quantity=1,
        )
        request = self._get_anonymous_request(session_key)
        cart = self.mixin.get_cart(request, product=self.product)
        self.assertEqual(cart, anon_cart)

    def test_get_cart_not_found(self):
        """Test get_cart returns None when not found"""
        request = self._get_authenticated_request()
        other_product = Products.objects.create(
            name="Other Product",
            slug="other-product",
            price=Decimal("50.00"),
            quantity=5,
            category=self.category,
            currency="UAH",
        )
        cart = self.mixin.get_cart(request, product=other_product)
        self.assertIsNone(cart)

    def test_get_cart_totals(self):
        """Test get_cart_totals returns correct totals"""
        request = self._get_authenticated_request()
        total_uah, total_usd = self.mixin.get_cart_totals(request)
        self.assertEqual(total_uah, round(self.cart.products_price(), 2))
        self.assertEqual(total_usd, round(self.cart.products_price_usd(), 2))

    def test_get_cart_data(self):
        """Test get_cart_data returns correct structure"""
        request = self._get_authenticated_request()
        data = self.mixin.get_cart_data(request)

        self.assertIn("items", data)
        self.assertIn("total_price", data)
        self.assertIn("total_price_usd", data)
        self.assertIn("total_quantity", data)

        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]
        self.assertEqual(item["id"], self.cart.id)
        self.assertEqual(item["product_id"], self.product.id)
        self.assertEqual(item["quantity"], 2)

    def test_get_cart_data_max_quantity_ready_to_ship(self):
        """Test max_quantity for ready_to_ship products"""
        request = self._get_authenticated_request()
        data = self.mixin.get_cart_data(request)
        item = data["items"][0]
        self.assertEqual(item["max_quantity"], self.product.quantity)

    def test_get_cart_data_max_quantity_last_item(self):
        """Test max_quantity for last_item products"""
        self.product.availability_status = "last_item"
        self.product.quantity = 10
        self.product.save()

        request = self._get_authenticated_request()
        data = self.mixin.get_cart_data(request)
        item = data["items"][0]
        self.assertEqual(item["max_quantity"], 5)

    def test_get_cart_data_max_quantity_out_of_stock(self):
        """Test max_quantity for out_of_stock products"""
        self.product.availability_status = "out_of_stock"
        self.product.save()

        request = self._get_authenticated_request()
        data = self.mixin.get_cart_data(request)
        item = data["items"][0]
        self.assertEqual(item["max_quantity"], 0)


class CartAddAPIViewTestCase(APITestCase):
    """Tests for CartAddAPIView"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
            availability_status="ready_to_ship",
        )
        self.url = reverse("carts:cart_add")

    def test_add_to_cart_authenticated(self):
        """Test adding product to cart for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_add_to_cart_anonymous(self):
        """Test adding product to cart for anonymous user"""
        session = self.client.session
        session.create()
        session.save()

        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_cart_without_product_id(self):
        """Test adding without product_id returns error"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"quantity": 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_nonexistent_product(self):
        """Test adding nonexistent product returns 404"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"product_id": 99999, "quantity": 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_out_of_stock_product(self):
        """Test adding out of stock product returns error"""
        self.product.availability_status = "out_of_stock"
        self.product.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_exceeds_stock_quantity(self):
        """Test adding more than available stock returns error"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": 100}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_updates_existing_cart(self):
        """Test adding to existing cart updates quantity"""
        Cart.objects.create(user=self.user, product=self.product, quantity=2)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": 3}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart.quantity, 5)

    def test_add_invalid_quantity_defaults_to_one(self):
        """Test invalid quantity defaults to 1"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": "invalid"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart.quantity, 1)

    def test_add_negative_quantity_defaults_to_one(self):
        """Test negative quantity defaults to 1"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": -5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart.quantity, 1)

    def test_add_last_item_max_quantity(self):
        """Test last_item product respects max 5 limit"""
        self.product.availability_status = "last_item"
        self.product.quantity = 10
        self.product.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"product_id": self.product.id, "quantity": 6}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartChangeAPIViewTestCase(APITestCase):
    """Tests for CartChangeAPIView"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
            availability_status="ready_to_ship",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )
        self.url = reverse("carts:cart_change")

    def test_change_quantity(self):
        """Test changing cart quantity"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"cart_id": self.cart.id, "quantity": 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.cart.refresh_from_db()
        self.assertEqual(self.cart.quantity, 5)

    def test_change_without_cart_id(self):
        """Test change without cart_id returns error"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"quantity": 5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_nonexistent_cart(self):
        """Test change nonexistent cart returns 404"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"cart_id": 99999, "quantity": 5})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_change_invalid_quantity(self):
        """Test invalid quantity defaults to 1"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"cart_id": self.cart.id, "quantity": "invalid"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.cart.refresh_from_db()
        self.assertEqual(self.cart.quantity, 1)

    def test_change_exceeds_max_quantity(self):
        """Test changing to quantity exceeding max returns error"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"cart_id": self.cart.id, "quantity": 100}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("max_quantity", response.data)

    def test_change_out_of_stock_product(self):
        """Test changing quantity of out_of_stock product"""
        self.product.availability_status = "out_of_stock"
        self.product.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url, {"cart_id": self.cart.id, "quantity": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartRemoveAPIViewTestCase(APITestCase):
    """Tests for CartRemoveAPIView"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )
        self.url = reverse("carts:cart_remove")

    def test_remove_cart_item(self):
        """Test removing cart item"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"cart_id": self.cart.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["quantity_deleted"], 2)
        self.assertFalse(Cart.objects.filter(id=self.cart.id).exists())

    def test_remove_without_cart_id(self):
        """Test remove without cart_id returns error"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_nonexistent_cart(self):
        """Test remove nonexistent cart returns 404"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"cart_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CartListAPIViewTestCase(APITestCase):
    """Tests for CartListAPIView"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )
        self.url = reverse("carts:cart_list")

    def test_get_cart_list(self):
        """Test getting cart list"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
        self.assertIn("total_price", response.data)
        self.assertIn("total_price_usd", response.data)
        self.assertIn("total_quantity", response.data)
        self.assertEqual(len(response.data["items"]), 1)

    def test_get_empty_cart_list(self):
        """Test getting empty cart list"""
        self.cart.delete()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 0)
        self.assertEqual(response.data["total_quantity"], 0)


class BasketAPIViewTestCase(APITestCase):
    """Tests for BasketAPIView"""

    @classmethod
    def setUpTestData(cls):
        cls.category = Categories.objects.create(name="Test Category", slug="test-cat")
        ExchangeRate.objects.create(
            base_currency="USD", target_currency="UAH", rate=Decimal("41.50")
        )

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            quantity=10,
            category=self.category,
            currency="UAH",
        )
        self.cart = Cart.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )
        self.url = reverse("carts:basket")

    def test_get_basket_json(self):
        """Test getting basket as JSON"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("items", response.data)
