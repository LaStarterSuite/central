# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""European VAT member-state metadata — the mirror of india_gst for EU billing.

A VAT registration number opens with the issuing country's 2-letter code, and
every member state sets its own standard rate, so both questions read here: the
billing profile can validate a VAT number against the billing country, and
pricing/seeding can pick up the standard rate. The checks are format-only —
confirming that a number actually exists in the EU's VIES registry is a separate,
rate-limited call nothing wires up yet.
"""

import re

# Member state -> the 2-letter code that opens its VAT numbers (ISO-3166 alpha-2,
# except Greece, which bills as EL). Names match the Country master.
VAT_COUNTRY_CODES = {
	"Austria": "AT",
	"Belgium": "BE",
	"Bulgaria": "BG",
	"Croatia": "HR",
	"Cyprus": "CY",
	"Czech Republic": "CZ",
	"Denmark": "DK",
	"Estonia": "EE",
	"Finland": "FI",
	"France": "FR",
	"Germany": "DE",
	"Greece": "EL",
	"Hungary": "HU",
	"Ireland": "IE",
	"Italy": "IT",
	"Latvia": "LV",
	"Lithuania": "LT",
	"Luxembourg": "LU",
	"Malta": "MT",
	"Netherlands": "NL",
	"Poland": "PL",
	"Portugal": "PT",
	"Romania": "RO",
	"Slovakia": "SK",
	"Slovenia": "SI",
	"Spain": "ES",
	"Sweden": "SE",
}

# Member state -> standard VAT rate (%) — the display/default rate, not a rate engine.
VAT_STANDARD_RATES = {
	"Austria": 20.0,
	"Belgium": 21.0,
	"Bulgaria": 20.0,
	"Croatia": 25.0,
	"Cyprus": 19.0,
	"Czech Republic": 21.0,
	"Denmark": 25.0,
	"Estonia": 24.0,
	"Finland": 25.5,
	"France": 20.0,
	"Germany": 19.0,
	"Greece": 24.0,
	"Hungary": 27.0,
	"Ireland": 23.0,
	"Italy": 22.0,
	"Latvia": 21.0,
	"Lithuania": 21.0,
	"Luxembourg": 17.0,
	"Malta": 18.0,
	"Netherlands": 21.0,
	"Poland": 23.0,
	"Portugal": 23.0,
	"Romania": 21.0,
	"Slovakia": 23.0,
	"Slovenia": 22.0,
	"Spain": 21.0,
	"Sweden": 25.0,
}

# A VAT number: 2-letter country code + 8-12 alphanumeric characters. Member states
# sharpen this to their own length and pattern; the umbrella format is all we check.
VAT_NUMBER_RE = re.compile(r"^[A-Z]{2}[0-9A-Z]{8,12}$")


def vat_country_options() -> list[str]:
	"""Member state names for a billing-address country dropdown (EU)."""
	return list(VAT_COUNTRY_CODES)


def vat_country_code(country: str | None) -> str | None:
	"""The 2-letter VAT code for a member state, or None if it is not a member."""
	return VAT_COUNTRY_CODES.get((country or "").strip())


def standard_vat_rate(country: str | None) -> float | None:
	"""The member state's standard VAT rate (%), or None if it is not a member."""
	return VAT_STANDARD_RATES.get((country or "").strip())


def is_member_state(country: str | None) -> bool:
	"""Whether the billing country is an EU member state."""
	return (country or "").strip() in VAT_COUNTRY_CODES


def vat_number_country(vat_number: str | None) -> str | None:
	"""The 2-letter code a VAT number claims ('FR...' -> 'FR'), or None when malformed."""
	number = _normalize_vat_number(vat_number)
	return number[:2] if VAT_NUMBER_RE.match(number) else None


def validate_vat_number(vat_number: str | None, country: str | None = None) -> bool:
	"""Format check: 2-letter code + 8-12 alphanumerics, and — when `country` is a
	member state — the code must be that country's own. No VIES call, so a
	format-valid number may still not exist."""
	number = _normalize_vat_number(vat_number)
	if not VAT_NUMBER_RE.match(number):
		return False
	code = vat_country_code(country)
	return code is None or number.startswith(code)


def _normalize_vat_number(vat_number: str | None) -> str:
	"""The VAT number as the format check reads it: trimmed, upper-cased."""
	return (vat_number or "").strip().upper()
