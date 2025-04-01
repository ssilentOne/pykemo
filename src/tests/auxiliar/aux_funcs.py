"""
Auxiliar functions tests module.
"""

from datetime import datetime
from unittest import TestCase

from src.pykemo._aux.aux_funcs import before_date, process_date, sanitize_data_url, since_date


class SanitizeDataURLTest(TestCase):

    def test_1_sanitize_correctly(self) -> None:
        path_a = {"path": "/ab/cd/12345678"}
        path_b = {"other": 1234}
        expected_a = {"path": "/data/ab/cd/12345678"}
        expected_b = {"other": 1234}

        sanitized_a = sanitize_data_url(path_a)
        sanitized_b = sanitize_data_url(path_b)

        self.assertEqual(sanitized_a.get("path", None), expected_a["path"])
        self.assertDictEqual(sanitized_a, expected_a)

        self.assertEqual(sanitized_b.get("path", None), None)
        self.assertDictEqual(sanitized_b, expected_b)


class ProcessDateTest(TestCase):

    def test_1_if_already_a_date_leave_as_is(self) -> None:
        normal_date = datetime(1234, 12, 21)

        processed_date = process_date(normal_date)

        self.assertEqual(processed_date, normal_date)
        # not only they are equal, they should be identical
        self.assertIs(processed_date, normal_date)


    def test_2_if_str_convert_to_datetime(self) -> None:
        date_str = "1234-12-21T12:34:56"
        expected_date = datetime(1234, 12, 21, 12, 34, 56)

        converted_date = process_date(date_str)

        self.assertEqual(converted_date, expected_date)


    def test_3_fail_if_incorrect_format(self) -> None:

        with self.assertRaises(ValueError):
            process_date("1234z56o78uT89:2")

        with self.assertRaises(ValueError):
            process_date("1234-12-34T12:34:56")

        with self.assertRaises(ValueError):
            # this is not the year 34, it should have leading zeroes like '0034'
            process_date("34-12-21T12:34:56")

        with self.assertRaises(ValueError):
            process_date("1234-12-21T12:34:56:0000")


    def test_4_convert_str_with_custom_formats(self) -> None:
        # due to datetime limitations, the date MUST include at least the day, month and year
        fmt_a = r"%Y-%m-%d--%H:%M"
        fmt_b = r"%d,%m,%Y"
        fmt_c = r"%m....%Y->%d"

        self.assertEqual(process_date("1964-5-21--14:56", fmt_a), datetime(1964, 5, 21, 14, 56))
        with self.assertRaises(ValueError):
            process_date("1964-5-21---14:56", fmt_a)

        self.assertEqual(process_date("7,3,2014", fmt_b), datetime(2014, 3, 7))
        with self.assertRaises(ValueError):
            process_date("007,3,2014", fmt_b)

        self.assertEqual(process_date("09....1888->17", fmt_c), datetime(1888, 9, 17))
        with self.assertRaises(ValueError):
            process_date("9...1888->17", fmt_c)


class DateComparationTest(TestCase):

    def test_1_check_if_before_without_format(self) -> None:
        before_a = datetime(1, 1, 1)
        before_b = datetime(2, 2, 2)
        after = datetime(2, 2, 2)

        self.assertTrue(before_date(before_a, after))
        # the comparation is strict
        self.assertFalse(before_date(before_b, after))


    def test_2_check_if_before_from_strings(self) -> None:
        before_a = "0005-06-07T12:34:56"
        after_a = datetime(9, 9, 9)
        before_b =  datetime(1, 2, 8)
        after_b = "0002-10-18T00:00:00"
        before_c = "0011-11-11T11:11:11"
        after_c = "0022-12-22T22:22:22"

        self.assertTrue(before_date(before_a, after_a))
        self.assertTrue(before_date(before_b, after_b))
        self.assertTrue(before_date(before_c, after_c))

        with self.assertRaises(ValueError):
            before_date(before_a, "lmao this is wrong date")

        with self.assertRaises(ValueError):
            before_date("lmao this is also wrong date", after_c)
