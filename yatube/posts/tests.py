from django.test import TestCase, Client


class TestStringMethods(TestCase):
    def test_length(self):
        self.assertEqual(len("yatube"), 6)

    def test_show_msg(self):
        self.assertTrue(False, msg="Важная проверка на истинность")
