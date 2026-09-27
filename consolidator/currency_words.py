"""Converts numbers in Indian numbering system to English currency words."""
import math

class IndianCurrencyWords:
    """Converts numeric values to formal Indian Currency words."""

    UNITS = [
        "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen"
    ]
    TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    @classmethod
    def _convert_two_digits(cls, n: int) -> str:
        if n == 0:
            return ""
        if n < 20:
            return cls.UNITS[n]
        tens = cls.TENS[n // 10]
        units = cls.UNITS[n % 10]
        return f"{tens} {units}".strip()

    @classmethod
    def _convert_three_digits(cls, n: int) -> str:
        if n == 0:
            return ""
        hundreds = n // 100
        remainder = n % 100
        words = []
        if hundreds > 0:
            words.append(f"{cls.UNITS[hundreds]} Hundred")
        if remainder > 0:
            words.append(cls._convert_two_digits(remainder))
        return " ".join(words)

    @classmethod
    def to_words(cls, amount: float) -> str:
        if amount == 0:
            return "Indian Rupees Zero Only"

        rupees = int(math.floor(amount))
        paise = int(round((amount - rupees) * 100))

        crores = rupees // 10000000
        rupees %= 10000000

        lakhs = rupees // 100000
        rupees %= 100000

        thousands = rupees // 1000
        rupees %= 1000

        remainder = rupees

        parts = []
        if crores > 0:
            parts.append(f"{cls._convert_two_digits(crores)} Crore")
        if lakhs > 0:
            parts.append(f"{cls._convert_two_digits(lakhs)} Lakh")
        if thousands > 0:
            parts.append(f"{cls._convert_two_digits(thousands)} Thousand")
        if remainder > 0:
            parts.append(cls._convert_three_digits(remainder))

        rupees_str = " ".join(parts).strip()
        paise_str = cls._convert_two_digits(paise) if paise > 0 else ""

        if rupees_str and paise_str:
            return f"Indian Rupees {rupees_str} and {paise_str} Paise Only"
        elif rupees_str:
            return f"Indian Rupees {rupees_str} Only"
        elif paise_str:
            return f"Indian Rupees Zero and {paise_str} Paise Only"
        return "Indian Rupees Zero Only"
