#     Copyright (C) 2018  Matthieu PETIOT
#
#     https://github.com/ardeidae/tasks-counter
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Tasks counter tests."""

import unittest
from counter import (weeks_for_year, WeekDay, Column,
                     weekday_from_date, seven_days_of_week)
from datetime import date


class TestWeeksForYear(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_year_is_a_string(self):
        self.assertIsNone(weeks_for_year("two thousand"))

    def test_year_is_a_number_in_string(self):
        self.assertEqual(52, weeks_for_year("2000"))

    def test_year_is_a_float(self):
        self.assertEqual(52, weeks_for_year(2000.43))

    def test_over_several_years(self):
        expected = {
            2000: 52,
            2001: 52,
            2002: 52,
            2003: 52,
            2004: 53,
            2005: 52,
            2006: 52,
            2007: 52,
            2008: 52,
            2009: 53,
            2010: 52,
            2011: 52,
            2012: 52,
            2013: 52,
            2014: 52,
            2015: 53,
            2016: 52,
            2017: 52,
            2018: 52,
            2019: 52,
            2020: 53,
            2021: 52,
            2022: 52,
            2023: 52,
            2024: 52,
            2025: 52,
            2026: 53,
            2027: 52,
            2028: 52,
            2029: 52,
            2030: 52,
        }

        for year, week in expected.items():
            with self.subTest(name='year {}'.format(year)):
                self.assertEqual(week, weeks_for_year(year))


class TestWeekDay(unittest.TestCase):

    def test_enum_values(self):
        self.assertEqual(0, WeekDay.Monday.value)
        self.assertEqual(1, WeekDay.Tuesday.value)
        self.assertEqual(2, WeekDay.Wednesday.value)
        self.assertEqual(3, WeekDay.Thursday.value)
        self.assertEqual(4, WeekDay.Friday.value)
        self.assertEqual(5, WeekDay.Saturday.value)
        self.assertEqual(6, WeekDay.Sunday.value)

    def test_enum_has_seven_days(self):
        self.assertEqual(7, len(WeekDay))

    def test_weekday_from_date_without_date(self):
        self.assertIsNone(weekday_from_date("a string"))

    def test_weekday_from_date(self):
        expected = {
            WeekDay.Monday: date(2018, 3, 5),
            WeekDay.Tuesday: date(2018, 3, 6),
            WeekDay.Wednesday: date(2018, 3, 7),
            WeekDay.Thursday: date(2018, 3, 8),
            WeekDay.Friday: date(2018, 3, 9),
            WeekDay.Saturday: date(2018, 3, 10),
            WeekDay.Sunday: date(2018, 3, 11),
        }
        for a_day, a_date in expected.items():
            with self.subTest(name='day {}'.format(a_day.name)):
                self.assertEqual(a_day, weekday_from_date(a_date))


class TestColumn(unittest.TestCase):

    def test_enum_values(self):
        self.assertEqual(0, Column.Id.value)
        self.assertEqual(1, Column.Task.value)
        self.assertEqual(2, Column.Start_Time.value)
        self.assertEqual(3, Column.End_Time.value)

    def test_enum_has_four_columns(self):
        self.assertEqual(4, len(Column))


class TestSevenDaysOfWeek(unittest.TestCase):

    def test_seven_days_of_week_with_week_too_big(self):
        self.assertEqual([], list(seven_days_of_week(2018, 54)))
        self.assertEqual([], list(seven_days_of_week(2018, 53)))
        self.assertNotEqual([], list(seven_days_of_week(2018, 52)))

    def test_args_are_string(self):
        self.assertEqual([], list(seven_days_of_week('str1', 'str2')))
        self.assertEqual([], list(seven_days_of_week('str1', 52)))
        self.assertEqual([], list(seven_days_of_week(2018, 'str2')))

    def test_args_are_number_in_string(self):
        self.assertEqual(7, len(list(seven_days_of_week('2018', '52'))))
        self.assertEqual(7, len(list(seven_days_of_week('2018', 52))))
        self.assertEqual(7, len(list(seven_days_of_week(2018, '52'))))

    def test_args_are_float(self):
        self.assertEqual(7, len(list(seven_days_of_week(2018.243, 52.13))))
        self.assertEqual(7, len(list(seven_days_of_week(2018.243, 52))))
        self.assertEqual(7, len(list(seven_days_of_week(2018, 52.13))))

    def test_week_number_is_less_than_one(self):
        self.assertEqual([], list(seven_days_of_week(2018, 0)))
        self.assertEqual([], list(seven_days_of_week(2018, -1)))
        self.assertEqual(7, len(list(seven_days_of_week(2018, 1))))

    def test_over_several_years_and_weeks(self):

        expected = {
            (2014, 52): (22, 12),
            (2015, 52): (21, 12),
            (2015, 53): (28, 12),
            (2016, 52): (26, 12),
            (2017, 52): (25, 12),
            (2018, 52): (24, 12),
            (2019, 1): (31, 12),
            (2018, 1): (1, 1),
            (2018, 2): (8, 1),
            (2018, 35): (27, 8),
            (2019, 38): (16, 9),
            (2016, 5): (1, 2),
            (2015, 14): (30, 3),
        }

        for (year, week), (day, month) in expected.items():
            with self.subTest(name='year {}, week {}'.format(year, week)):
                generator = seven_days_of_week(year, week)
                monday = next(generator)
                self.assertEqual(month, monday.month)
                self.assertEqual(day, monday.day)

    def test_sequence_of_days(self):

        generator = seven_days_of_week(2018, 10)

        monday = next(generator)
        self.assertEqual(3, monday.month)
        self.assertEqual(5, monday.day)
        self.assertEqual(2018, monday.year)

        tuesday = next(generator)
        self.assertEqual(3, tuesday.month)
        self.assertEqual(6, tuesday.day)
        self.assertEqual(2018, tuesday.year)

        wednesday = next(generator)
        self.assertEqual(3, wednesday.month)
        self.assertEqual(7, wednesday.day)
        self.assertEqual(2018, wednesday.year)

        thursday = next(generator)
        self.assertEqual(3, thursday.month)
        self.assertEqual(8, thursday.day)
        self.assertEqual(2018, thursday.year)

        friday = next(generator)
        self.assertEqual(3, friday.month)
        self.assertEqual(9, friday.day)
        self.assertEqual(2018, friday.year)

        saturday = next(generator)
        self.assertEqual(3, saturday.month)
        self.assertEqual(10, saturday.day)
        self.assertEqual(2018, saturday.year)

        sunday = next(generator)
        self.assertEqual(3, sunday.month)
        self.assertEqual(11, sunday.day)
        self.assertEqual(2018, sunday.year)

        with self.assertRaises(StopIteration):
            next(generator)


if __name__ == '__main__':
    unittest.main()
