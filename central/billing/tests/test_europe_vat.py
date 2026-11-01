# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Format-level tests for the EU VAT metadata — pure stdlib, no site needed."""

import unittest

from central.billing.europe_vat import (
	VAT_STANDARD_RATES,
	is_member_state,
	standard_vat_rate,
	validate_vat_number,
	vat_country_code,
	vat_country_options,
	vat_number_country,
)


class TestVatCountryMetadata(unittest.TestCase):
	def test_every_member_state_has_a_code_and_a_rate(self):
		for country in vat_country_options():
			self.assertRegex(vat_country_code(country), r"^[A-Z]{2}$")
			self.assertGreater(standard_vat_rate(country), 0)

	def test_country_codes(self):
		self.assertEqual(vat_country_code("France"), "FR")
		self.assertEqual(vat_country_code("Greece"), "EL")  # Greece bills as EL, not GR
		self.assertEqual(vat_country_code("Czech Republic"), "CZ")  # the Country-master name
		self.assertIsNone(vat_country_code("India"))
		self.assertIsNone(vat_country_code(""))

	def test_standard_rates(self):
		self.assertEqual(standard_vat_rate("France"), 20.0)
		self.assertEqual(standard_vat_rate("Germany"), 19.0)
		self.assertIsNone(standard_vat_rate("Switzerland"))

	def test_rate_boundaries(self):
		self.assertEqual(min(VAT_STANDARD_RATES.values()), 17.0)  # Luxembourg
		self.assertEqual(max(VAT_STANDARD_RATES.values()), 27.0)  # Hungary

	def test_membership(self):
		self.assertTrue(is_member_state("Spain"))
		self.assertFalse(is_member_state("United Kingdom"))
		self.assertFalse(is_member_state(None))


class TestVatNumberFormat(unittest.TestCase):
	def test_valid_numbers_per_country(self):
		self.assertTrue(validate_vat_number("FR40303265045", "France"))  # FR + 11 alphanumerics
		self.assertTrue(validate_vat_number("DE136695976", "Germany"))  # DE + 9 digits
		self.assertTrue(validate_vat_number("IE6388047V", "Ireland"))  # shortest member format
		self.assertTrue(validate_vat_number("  fr40303265045 ", "France"))  # trimmed, case-free

	def test_prefix_must_match_the_billing_country(self):
		self.assertFalse(validate_vat_number("DE136695976", "France"))
		self.assertTrue(validate_vat_number("DE136695976", None))  # no country: format only
		self.assertTrue(validate_vat_number("DE136695976", "United States"))  # not a member

	def test_invalid_formats(self):
		self.assertFalse(validate_vat_number(None))
		self.assertFalse(validate_vat_number(""))
		self.assertFalse(validate_vat_number("40303265045"))  # no country code
		self.assertFalse(validate_vat_number("F40303265045"))  # one-letter code
		self.assertFalse(validate_vat_number("FR4030326"))  # 7 characters after the code
		self.assertFalse(validate_vat_number("FR4030326504512"))  # 13 after the code
		self.assertFalse(validate_vat_number("FR 40303265045"))  # embedded space
		self.assertFalse(validate_vat_number("FR40303265045#"))  # punctuation

	def test_country_extraction(self):
		self.assertEqual(vat_number_country("FR40303265045"), "FR")
		self.assertEqual(vat_number_country("de136695976"), "DE")
		self.assertIsNone(vat_number_country("DE13669"))  # too short to be well-formed
		self.assertIsNone(vat_number_country(None))


if __name__ == "__main__":
	unittest.main()
