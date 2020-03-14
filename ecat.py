from utilities import get_date_range_from_year_and_week


def main():
    print("Evil Corp Activity Tracker")
    for y in range(1, 52):
        print((get_date_range_from_year_and_week(2020, y)))


if __name__ == "__main__":
    main()
