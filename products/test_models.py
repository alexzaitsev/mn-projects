from django.test import TestCase

from producthuntclone.test_utils import *


class ProductTests(TestCase):
    def test_summary_shows_body_if_body_len_is_le_100(self):
        """
        If `body` length is 100 or less symbols -
        `summary()` returns it unchanged.
        """
        body = 'less then 100 symbols'
        create_test_user_with_endpoint(self.client)
        product = create_test_product(self.client, body=body)
        self.assertEqual(product.summary(), body)

    def test_summary_shows_first_100_symbols_and_3_dots_if_body_len_is_gt_100(self):
        """
        If `body` length is greater than 100 symbols -
        `summary()` returns first 100 symbols, strips them
        and adds 3 dots.
        """
        body = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        create_test_user_with_endpoint(self.client)
        product = create_test_product(self.client, body=body)
        self.assertEqual(product.summary(), f'{body[:100].strip()}...')
