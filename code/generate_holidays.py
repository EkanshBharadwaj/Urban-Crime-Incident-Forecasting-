import pandas as pd

# Requires: pip install holidays
import holidays
from dateutil.easter import easter
import holidays.calendars.islamic as islamic_cal
import holidays.calendars.hebrew as hebrew_cal
import holidays.calendars.hindu as hindu_cal


def main():
    start_date = "2006-01-01"
    end_date = "2024-12-31"
    output_path = "Datasets/Clean/Holidays.csv"

    dates = pd.date_range(start_date, end_date, freq="D")

    # US federal holidays (statutory)
    us_holidays = holidays.US(years=range(2006, 2025))

    # Major religious holidays (customize as needed)
    years = list(range(2006, 2025))

    # Christian: Christmas + Easter Sunday + Good Friday
    christian_dates = set()
    for y in years:
        christmas = pd.Timestamp(year=y, month=12, day=25).date()
        easter_sun = easter(y)
        good_friday = easter_sun - pd.Timedelta(days=2)
        christian_dates.update([christmas, easter_sun, good_friday])

    # Islamic: Eid al-Fitr + Eid al-Adha (from holidays calendars)
    islamic_dates = set()
    isl = islamic_cal._IslamicLunar()
    for y in years:
        for d, _confirmed in isl.eid_al_fitr_dates(y):
            if d.year in (y - 1, y, y + 1):
                islamic_dates.add(d)
        for d, _confirmed in isl.eid_al_adha_dates(y):
            if d.year in (y - 1, y, y + 1):
                islamic_dates.add(d)

    # Jewish: Rosh Hashanah + Yom Kippur + Passover
    jewish_dates = set()
    heb = hebrew_cal._HebrewLunisolar()
    for y in years:
        jewish_dates.add(heb.rosh_hashanah_date(y))
        jewish_dates.add(heb.yom_kippur_date(y))
        jewish_dates.add(heb.passover_date(y))

    # Hindu: Diwali (India date) + Holi
    hindu_dates = set()
    hin = hindu_cal._HinduLunisolar()
    for y in years:
        diwali_date, _ = hin.diwali_india_date(y)
        holi_date, _ = hin.holi_date(y)
        hindu_dates.update([diwali_date, holi_date])

    weekend = (dates.weekday >= 5).astype(int)
    holiday = dates.isin(pd.to_datetime(list(us_holidays.keys()))).astype(int)

    def build_detail(d):
        labels = []
        if d.weekday() >= 5:
            labels.append("Weekend")
        if d in us_holidays:
            labels.append(us_holidays[d])
        if d in christian_dates:
            if d.month == 12 and d.day == 25:
                labels.append("Christmas")
            else:
                # Easter or Good Friday
                if d == easter(d.year):
                    labels.append("Easter")
                else:
                    labels.append("Good Friday")
        if d in islamic_dates:
            labels.append("Islamic Holiday (Eid)")
        if d in jewish_dates:
            # Identify specific Jewish holiday if possible
            if d == heb.rosh_hashanah_date(d.year):
                labels.append("Rosh Hashanah")
            elif d == heb.yom_kippur_date(d.year):
                labels.append("Yom Kippur")
            elif d == heb.passover_date(d.year):
                labels.append("Passover")
            else:
                labels.append("Jewish Holiday")
        if d in hindu_dates:
            # Diwali or Holi
            diwali_date, _ = hin.diwali_india_date(d.year)
            holi_date, _ = hin.holi_date(d.year)
            if d == diwali_date:
                labels.append("Diwali")
            elif d == holi_date:
                labels.append("Holi")
            else:
                labels.append("Hindu Holiday")
        return " + ".join(labels)

    df = pd.DataFrame(
        {
            "date": dates.date,
            "weekend": weekend,
            "holiday": holiday,  # matches parent paper's statutory holiday flag
            "is_christian_holiday": [1 if d.date() in christian_dates else 0 for d in dates],
            "is_islamic_holiday": [1 if d.date() in islamic_dates else 0 for d in dates],
            "is_jewish_holiday": [1 if d.date() in jewish_dates else 0 for d in dates],
            "is_hindu_holiday": [1 if d.date() in hindu_dates else 0 for d in dates],
            "holiday_detail": [build_detail(d.date()) for d in dates],
        }
    )

    df.to_csv(output_path, index=False)
    print(f"Wrote {output_path} with {len(df)} rows.")


if __name__ == "__main__":
    main()
