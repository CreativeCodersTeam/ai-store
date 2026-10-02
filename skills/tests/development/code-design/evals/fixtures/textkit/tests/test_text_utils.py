import unittest

from textkit.text_utils import normalize_whitespace, strip_accents, strip_tags, truncate_words


class TextUtilsTests(unittest.TestCase):
    def test_normalize_whitespace(self):
        self.assertEqual(normalize_whitespace("  a \n\t b  "), "a b")

    def test_strip_tags(self):
        self.assertEqual(strip_tags("<p>Hallo <b>Welt</b></p>"), "Hallo Welt")

    def test_truncate_words_keeps_short_text(self):
        self.assertEqual(truncate_words("kurz", 10), "kurz")

    def test_truncate_words_does_not_cut_words(self):
        self.assertEqual(truncate_words("Der schnelle braune Fuchs", 15), "Der schnelle…")

    def test_strip_accents(self):
        self.assertEqual(strip_accents("Café Müller"), "Cafe Muller")


if __name__ == "__main__":
    unittest.main()
