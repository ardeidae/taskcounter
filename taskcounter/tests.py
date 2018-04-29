#     Copyright (C) 2018  Matthieu PETIOT
#
#     https://github.com/ardeidae/taskcounter
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

"""Task counter tests."""

import unittest
from datetime import date

from .counter import (Column, ResultColumn, WeekDay, minutes_to_time,
                      minutes_to_time_str, seven_days_of_week,
                      weekday_from_date, weeks_for_year)


class TestWeeksForYear(unittest.TestCase):
    """Tests for weeks_for_year function."""

    def test_non_number_string_returns_none(self):
        """Test that non number string returns None."""
        self.assertIsNone(weeks_for_year("two thousand"))

    def test_int_in_string_returns_correct_value(self):
        """Test that int in string returns correct value."""
        self.assertEqual(52, weeks_for_year("2000"))

    def test_float_value_returns_correct_value(self):
        """Test that float value returns correct value."""
        self.assertEqual(52, weeks_for_year(2000.43))

    def test_none_returns_none(self):
        """Test that None returns None."""
        self.assertIsNone(weeks_for_year(None))

    def test_number_of_weeks_for_several_years(self):
        """Test number of weeks for several years."""
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
    """Tests for WeekDay enum ans weekday_from_date."""

    def test_enum_values(self):
        """Test enum values."""
        self.assertEqual(0, WeekDay.Monday.value)
        self.assertEqual(1, WeekDay.Tuesday.value)
        self.assertEqual(2, WeekDay.Wednesday.value)
        self.assertEqual(3, WeekDay.Thursday.value)
        self.assertEqual(4, WeekDay.Friday.value)
        self.assertEqual(5, WeekDay.Saturday.value)
        self.assertEqual(6, WeekDay.Sunday.value)

    def test_enum_has_seven_days(self):
        """Test that enum has seven days."""
        self.assertEqual(7, len(WeekDay))

    def test_non_number_string_returns_none(self):
        """Test that non number string returns None."""
        self.assertIsNone(weekday_from_date("a string"))

    def test_a_date_returns_the_right_weekday(self):
        """Test that a date returns the right weekday."""
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
    """Tests for Column enum."""

    def test_enum_values(self):
        """Test enum values."""
        self.assertEqual(0, Column.Id.value)
        self.assertEqual(1, Column.Task.value)
        self.assertEqual(2, Column.Start_Time.value)
        self.assertEqual(3, Column.End_Time.value)

    def test_enum_has_four_columns(self):
        """Test that enum has four columns."""
        self.assertEqual(4, len(Column))


class TestResultColumn(unittest.TestCase):
    """Tests for Result Column enul."""

    def test_enum_values(self):
        """Test enum values."""
        self.assertEqual(0, ResultColumn.Task.value)
        self.assertEqual(1, ResultColumn.Time.value)
        self.assertEqual(2, ResultColumn.Man_Day.value)

    def test_enum_has_three_columns(self):
        """Test that enum has two columns."""
        self.assertEqual(3, len(ResultColumn))


class TestSevenDaysOfWeek(unittest.TestCase):
    """Tests for seven_days_of_week function."""

    def test_number_of_weeks_too_big_returns_empty(self):
        """Test that number of weeks too big returns empty."""
        self.assertEqual([], list(seven_days_of_week(2018, 54)))
        self.assertEqual([], list(seven_days_of_week(2018, 53)))
        self.assertNotEqual([], list(seven_days_of_week(2018, 52)))

    def test_non_number_string_returns_empty(self):
        """Test that non number string returns empty."""
        self.assertEqual([], list(seven_days_of_week('str1', 'str2')))
        self.assertEqual([], list(seven_days_of_week('str1', 52)))
        self.assertEqual([], list(seven_days_of_week(2018, 'str2')))

    def test_int_in_string_returns_seven_days_list(self):
        """Test that int in string returns seven days list.."""
        self.assertEqual(7, len(list(seven_days_of_week('2018', '52'))))
        self.assertEqual(7, len(list(seven_days_of_week('2018', 52))))
        self.assertEqual(7, len(list(seven_days_of_week(2018, '52'))))

    def test_float_returns_seven_days_list(self):
        """Test that float returns seven days list."""
        self.assertEqual(7, len(list(seven_days_of_week(2018.243, 52.13))))
        self.assertEqual(7, len(list(seven_days_of_week(2018.243, 52))))
        self.assertEqual(7, len(list(seven_days_of_week(2018, 52.13))))

    def test_negative_week_number_returns_empty(self):
        """Test that negative week number returns empty."""
        self.assertEqual([], list(seven_days_of_week(2018, 0)))
        self.assertEqual([], list(seven_days_of_week(2018, -1)))
        self.assertEqual(7, len(list(seven_days_of_week(2018, 1))))

    def test_none_returns_none(self):
        """Test that None returns None."""
        self.assertEqual([], list(seven_days_of_week(None, None)))
        self.assertEqual([], list(seven_days_of_week(2018, None)))
        self.assertEqual([], list(seven_days_of_week(None, 15)))

    def test_a_couple_week_and_year_returns_the_right_monday(self):
        """Test that a couple week/year returns the right monday."""
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

    def test_a_couple_week_and_year_returns_the_right_sequence_of_days(self):
        """Test that a couple week/year returns the right sequence of days."""
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


class TestMinutesToTime(unittest.TestCase):
    """Tests for minutes_to_time function."""

    def test_negative_returns_none(self):
        """Test that negative returns None."""
        self.assertIsNone(minutes_to_time(-1))

    def test_none_returns_none(self):
        """Test that None returns None."""
        self.assertIsNone(minutes_to_time(None))

    def test_float_returns_correct_value(self):
        """Test that float returns correct value."""
        self.assertEqual(minutes_to_time(50.3), (0, 50))

    def test_int_int_string_returns_correct_value(self):
        """Test that int in string returns correct value."""
        self.assertEqual(minutes_to_time('50'), (0, 50))

    def test_non_number_string_returns_none(self):
        """Test that non number string returns None."""
        self.assertIsNone(minutes_to_time('a string'))

    def test_zero_minutes_returns_0_0(self):
        """Test that zero minutes returns 00:00."""
        self.assertEqual(minutes_to_time(0), (0, 0))

    def test_less_than_60_minutes_returns_less_than_one_hour(self):
        """Test that less than 60 minutes returns less than one hour."""
        self.assertEqual(minutes_to_time(50), (0, 50))

    def test_60_minutes_returns_exactly_one_hour(self):
        """Test that 60 minutes returns exactly one hour."""
        self.assertEqual(minutes_to_time(60), (1, 0))

    def test_more_than_60_minutes_returns_more_than_one_hour(self):
        """Test that more than 60 minutes returns more than one hour."""
        self.assertEqual(minutes_to_time(65), (1, 5))

    def test_time_result_with_more_than_10_hours(self):
        """Test time result with more than 10 hours."""
        self.assertEqual(minutes_to_time(645), (10, 45))


class TestMinutesToTimeStr(unittest.TestCase):
    """Tests for minutes_to_time_str function."""

    def test_negative_returns_none(self):
        """Test that negative returns None."""
        self.assertIsNone(minutes_to_time_str(-1))

    def test_none_returns_none(self):
        """Test that None returns None."""
        self.assertIsNone(minutes_to_time_str(None))

    def test_float_returns_correct_value(self):
        """Test that float returns correct value."""
        self.assertEqual(minutes_to_time_str(50.3), '00:50')

    def test_int_int_string_returns_correct_value(self):
        """Test that int in string returns correct value."""
        self.assertEqual(minutes_to_time_str('50'), '00:50')

    def test_non_number_string_returns_none(self):
        """Test that non number string returns None."""
        self.assertIsNone(minutes_to_time_str('a string'))

    def test_zero_minutes_returns_00_00(self):
        """Test that zero minutes returns 00:00."""
        self.assertEqual(minutes_to_time_str(0), '00:00')

    def test_less_than_60_minutes_returns_less_than_one_hour(self):
        """Test that less than 60 minutes returns less than one hour."""
        self.assertEqual(minutes_to_time_str(50), '00:50')

    def test_60_minutes_returns_exactly_one_hour(self):
        """Test that 60 minutes returns exactly one hour."""
        self.assertEqual(minutes_to_time_str(60), '01:00')

    def test_more_than_60_minutes_returns_more_than_one_hour(self):
        """Test that more than 60 minutes returns more than one hour."""
        self.assertEqual(minutes_to_time_str(65), '01:05')

    def test_time_result_without_zero_padded_values(self):
        """Test time result without zero padded values."""
        self.assertEqual(minutes_to_time_str(645), '10:45')


if __name__ == '__main__':
    unittest.main()
