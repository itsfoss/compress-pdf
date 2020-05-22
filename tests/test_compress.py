import compress_pdf
import os
import unittest

from unittest.mock import patch

path = os.path.dirname(os.path.abspath(__file__))

class TestPdf(unittest.TestCase):
    '''Test the compress function with a dummy file'''
    def test_compress_success_preprint(self):
        compress_pdf.compress(f"{path}/data/dummy.pdf", 1)

    def test_compress_success_screen(self):
        compress_pdf.compress(f"{path}/data/dummy.pdf", 2)

    def test_compress_success_ebook(self):
        compress_pdf.compress(f"{path}/data/dummy.pdf", 3)

    def tearDown(self):
        os.remove(f"{path}/data/dummy-compressed.pdf")