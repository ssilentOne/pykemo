"""
Auxiliar functions tests module.
"""

from datetime import datetime
from random import randint
from unittest import TestCase

from src.pykemo._aux.aux_funcs import (
    DEFAULT_PAGE_SIZE,
    before_date,
    parse_tags,
    process_date,
    query_params,
    sanitize_data_url,
    sanitize_str,
    since_date,
)


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


    def test_3_check_if_before_with_custom_formats(self) -> None:
        before_a = "0001-01-01"
        before_a_fmt = r"%Y-%m-%d"
        after_a = datetime(2, 1, 12)
        before_b = datetime(2000, 9, 9)
        after_b = "11-_99,.23"
        after_b_fmt = r"%m-_%y,.%d"

        self.assertTrue(before_date(before_a, after_a, fmt1=before_a_fmt))
        self.assertFalse(before_date(before_b, after_b, fmt2=after_b_fmt))


    def test_4_check_if_before_fails_with_custom_formats(self) -> None:
        before = "01-01-01"
        before_fmt = r"%Y-%m-%d"
        after = datetime(2, 1, 12)

        with self.assertRaises(ValueError):
            before_date(before, after, fmt1=before_fmt)


    def test_5_check_if_since_without_format(self) -> None:
        after_a = datetime(10, 10, 10)
        after_b = datetime(5, 5, 5)
        before = datetime(5, 5, 5)

        self.assertTrue(since_date(after_a, before))
        # the comparation is not strict: it checks greater or equal
        self.assertTrue(since_date(after_b, before))


    def test_6_check_if_since_from_strings(self) -> None:
        incorrect_before_a = datetime(9, 9, 9)
        incorrect_after_a = "0005-06-07T12:34:56"
        before_b =  datetime(1, 2, 8)
        after_b = "0002-10-18T00:00:00"
        before_c = "0011-11-11T11:11:11"
        after_c = "0022-12-22T22:22:22"

        self.assertFalse(since_date(incorrect_after_a, incorrect_before_a))
        self.assertTrue(since_date(after_b, before_b))
        self.assertTrue(since_date(after_c, before_c))

        with self.assertRaises(ValueError):
            since_date(before_b, "lmao this is wrong date")

        with self.assertRaises(ValueError):
            since_date("lmao this is also wrong date", after_c)


    def test_7_check_if_since_with_custom_formats(self) -> None:
        before_a = "0001-01-01"
        before_a_fmt = r"%Y-%m-%d"
        after_a = datetime(2, 1, 12)
        before_b = datetime(2000, 9, 9)
        after_b = "11-_99,.23"
        after_b_fmt = r"%m-_%y,.%d"

        self.assertTrue(since_date(after_a, before_a, fmt2=before_a_fmt))
        self.assertFalse(since_date(after_b, before_b, fmt1=after_b_fmt))


    def test_8_check_if_since_fails_with_custom_formats(self) -> None:
        before = "01-01-01"
        before_fmt = r"%Y-%m-%d"
        after = datetime(2, 1, 12)

        with self.assertRaises(ValueError):
            since_date(after, before, fmt2=before_fmt)


    def test_9_before_and_since_are_always_opposites(self) -> None:
        before_a = datetime(1, 1, 1)
        after_a = datetime(2, 2, 2)
        before_b = datetime(3, 3, 3)
        after_b = datetime(3, 3, 3)

        self.assertNotEqual(before_date(before_a, after_a), since_date(before_a, after_a))
        self.assertNotEqual(before_date(before_b, after_b), since_date(before_b, after_b))


class StringSanitizerTest(TestCase):

    def test_1_removes_oopsies_correctly(self) -> None:
        raw = "Hello, world!"
        expected_a = "Hello world"
        expected_b = "Hello. world."
        expected_c = "He--o,-wor-d!"

        self.assertEqual(sanitize_str(raw, (",", "!"), ""), expected_a)
        self.assertEqual(sanitize_str(raw, (",", "!"), "."), expected_b)
        self.assertEqual(sanitize_str(raw, ("l", " "), "-"), expected_c)


    def test_2_if_str_is_legal_then_leave_as_is(self) -> None:
        raw = "your mom"

        processed = sanitize_str(raw, ("!", ",", "(", ")"), "")

        self.assertEqual(processed, raw)


    def test_3_if_none_forbidden_chars_then_leave_as_is(self) -> None:
        raw = "Hello mom!"

        processed = sanitize_str(raw, (), "")

        self.assertEqual(processed, raw)


class QueryParamsTest(TestCase):

    def test_1_format_query_correctly(self) -> None:
        query = "something_something"
        expected = [("q", query)]

        params = query_params(query=query)

        self.assertListEqual(params, expected)


    def test_2_format_offset_correctly(self) -> None:
        offset = DEFAULT_PAGE_SIZE * 2 # must be a multiple of this constant
        expected = [("o", offset)]

        params = query_params(offset=offset)

        self.assertListEqual(params, expected)


    def test_3_raise_exception_if_incorrect_offset(self) -> None:
        offset = 32

        with self.assertRaises(ValueError):
            query_params(offset=offset)


    def test_4_format_with_random_offsets(self) -> None:
        for _ in range(500):
            offset = randint(1, DEFAULT_PAGE_SIZE * 100)

            if offset % DEFAULT_PAGE_SIZE == 0:
                self.assertListEqual(query_params(offset=offset), [("o", offset)])
            else:
                with self.assertRaises(ValueError):
                    query_params(offset=offset)


    def test_5_format_with_custom_steppings(self) -> None:
        stepping_1 = 800
        stepping_2 = 85

        self.assertListEqual(query_params(offset=0, stepping=stepping_1), [("o", 0)])
        self.assertListEqual(query_params(offset=2400, stepping=stepping_1), [("o", 2400)])
        with self.assertRaises(ValueError):
            query_params(offset=76, stepping=stepping_2)

        self.assertListEqual(query_params(offset=170, stepping=stepping_2), [("o", 170)])
        self.assertListEqual(query_params(offset=8500, stepping=stepping_2), [("o", 8500)])
        with self.assertRaises(ValueError):
            query_params(offset=90, stepping=stepping_2)


    def test_6_format_tags_correctly(self) -> None:
        tag_1 = "haha"
        tag_2 = "heehee"
        tag_3 = "..."

        # order shouldn't matter for what it's used, but this specific function preserves
        # the relative order just in case
        expected = [("tag", tag_1), ("tag", tag_2), ("tag", tag_3)]

        self.assertListEqual(query_params(tags=[tag_1, tag_2, tag_3]), expected)


    def test_7_format_with_query_offset_and_tags(self) -> None:
        query = "your mom"
        offset = DEFAULT_PAGE_SIZE * 4
        tags = ["spam", "eggs"]
        # in this relative order
        expected = [("q", query), ("o", offset), ("tag", "spam"), ("tag", "eggs")]

        params = query_params(query=query, offset=offset, tags=tags)

        self.assertListEqual(params, expected)


class TagsParserTest(TestCase):

    def test_1_remove_leading_chars(self) -> None:
        raw = r"{tag"
        expected = ["tag"]

        self.assertListEqual(parse_tags(raw), expected)


    def test_2_remove_trailing_chars(self) -> None:
        raw = r"tag}"
        expected = ["tag"]

        self.assertListEqual(parse_tags(raw), expected)


    def test_3_remove_both_leading_and_trailing_chars(self) -> None:
        raw = r"{tag}"
        expected = ["tag"]

        self.assertListEqual(parse_tags(raw), expected)


    def test_4_separate_into_multiple_tags(self) -> None:
        raw_1 = r"{tag_1,tag_2,tag_3"
        raw_2 = r"tag_1,tag_2,tag_3}"
        raw_3 = r"{tag_1,tag_2,tag_3}"
        expected = ["tag_1", "tag_2", "tag_3"]

        self.assertListEqual(parse_tags(raw_1), expected)
        self.assertListEqual(parse_tags(raw_2), expected)
        self.assertListEqual(parse_tags(raw_3), expected)
