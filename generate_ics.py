import sys
import os
from typing import Optional

sys.path.append(os.path.pardir)

from my_school_menus.msm_api import Menus
from my_school_menus.msm_calendar import Calendar

DEFAULT_DISTRICT_ID = 99
DEFAULT_MENU_ID = 104901
DEFAULT_FILE_SUFFIX = 'school-lunch-calendar.ics'
DEFAULT_OUTPUT_FILENAME = 'school-lunch.ics'


def env_int(name: str, default: Optional[int]) -> Optional[int]:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc


DISTRICT_ID = env_int("DISTRICT_ID", DEFAULT_DISTRICT_ID)
MENU_ID = env_int("MENU_ID", DEFAULT_MENU_ID)
FILE_SUFFIX = os.getenv("FILE_SUFFIX", DEFAULT_FILE_SUFFIX)
OUTPUT_MODE = os.getenv("OUTPUT_MODE", "combined").lower()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.dirname(os.path.realpath(__file__)))
OUTPUT_FILENAME = os.getenv("OUTPUT_FILENAME", DEFAULT_OUTPUT_FILENAME)


def main():
    if not DISTRICT_ID or not MENU_ID:
        raise ValueError("DISTRICT_ID and MENU_ID are required to generate calendars.")

    menus = Menus()
    menu = menus.get(district_id=DISTRICT_ID, menu_id=MENU_ID)
    available_dates = sorted(menus.menu_months(menu))

    if OUTPUT_MODE not in ("combined", "monthly"):
        raise ValueError("OUTPUT_MODE must be 'combined' or 'monthly'.")

    cal = Calendar()

    if OUTPUT_MODE == "combined":
        all_events = []
        for date in available_dates:
            calendar_menu = menus.get(
                district_id=DISTRICT_ID, menu_id=MENU_ID, date=date
            )
            events = cal.events(calendar_menu)
            all_events.extend(events)
        calendar = cal.calendar(all_events)
        ical = cal.ical(calendar)
        filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        print(f"Writing combined calendar to {filepath}")
        with open(filepath, 'w') as f:
            f.write(ical)
        print('Calendar file written successfully!')
        return

    for date in available_dates:
        filepath = os.path.join(OUTPUT_DIR, f"{date.year}-{date.month:02}-{FILE_SUFFIX}")
        calendar_menu = menus.get(
            district_id=DISTRICT_ID, menu_id=MENU_ID, date=date
        )
        events = cal.events(calendar_menu)
        calendar = cal.calendar(events)
        ical = cal.ical(calendar)
        print(f"Writing calendar file to {filepath}")
        with open(filepath, 'w') as f:
            f.write(ical)
        print('Calendar file written successfully!')


if __name__ == '__main__':
    main()
