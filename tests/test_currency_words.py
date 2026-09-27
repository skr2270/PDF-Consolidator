"""Unit tests for Indian Currency Words converter."""
import pytest
from consolidator.currency_words import IndianCurrencyWords

def test_zero():
    assert IndianCurrencyWords.to_words(0) == "Indian Rupees Zero Only"

def test_exact_lakhs():
    words = IndianCurrencyWords.to_words(240909.00)
    assert "Two Lakh" in words
    assert "Forty Thousand" in words
    assert "Nine Hundred Nine" in words

def test_paise():
    words = IndianCurrencyWords.to_words(601808.50)
    assert "Six Lakh" in words
    assert "Fifty Paise Only" in words

def test_crores():
    words = IndianCurrencyWords.to_words(2002536.00)
    assert "Twenty Lakh" in words
    assert "Two Thousand" in words
    assert "Five Hundred Thirty Six" in words
