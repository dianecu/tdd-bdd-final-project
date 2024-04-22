# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        result = Product.find(product.id)
        self.assertEqual(result.id, product.id)
        self.assertEqual(result.name, product.name)
        self.assertEqual(result.description, product.description)
        self.assertEqual(Decimal(result.price), product.price)
        self.assertEqual(result.available, product.available)
        self.assertEqual(result.category, product.category)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        product.description = "Popocatepetl"
        product.update()
        found = Product.find(product.id)
        self.assertEqual(product.id, found.id)
        self.assertEqual(product.description, "Popocatepetl")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, product.id)
        self.assertEqual(products[0].description, "Popocatepetl")

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create five Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_a_product_by_name(self):
        """It should Find a Product by Name"""
        product = [ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory()]
        # Create 5 products
        for i in range(5):
            product[i].create()

        name = product[0].name
        contador = 0
        for i in range(5):
            if (name == product[i].name):
                contador += 1

        same_name = Product.find_by_name(name)
        self.assertEqual(same_name.count(), contador)
        for product in same_name:
            self.assertEqual(product.name, name)

    def test_find_a_product_by_availability(self):
        """It should Find a Product by Availability"""
        product = [ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(),
                   ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory()]
        # Create 10 products
        for i in range(10):
            product[i].create()

        available = product[0].available
        contador = 0
        for i in range(10):
            if (available == product[i].available):
                contador += 1

        specified_availability = Product.find_by_availability(available)
        self.assertEqual(specified_availability.count(), contador)
        for product in specified_availability:
            self.assertEqual(product.available, available)

    def test_find_a_product_by_category(self):
        """It should Find a Product by Category"""
        product = [ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(),
                   ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory(), ProductFactory()]
        # Create 10 products
        for i in range(10):
            product[i].create()

        category = product[0].category
        contador = 0
        for i in range(10):
            if (category == product[i].category):
                contador += 1

        result_category = Product.find_by_category(category)
        self.assertEqual(result_category.count(), contador)
        for product in result_category:
            self.assertEqual(product.category, category)
