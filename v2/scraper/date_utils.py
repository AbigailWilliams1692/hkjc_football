###################################################
# Project: HKJC Football
# Script: scraper/match_records_scraper.py
# Description: scraper class for match results
# Author: AbigailWilliams
# Date: 2025-01-24
###################################################

###################################################
# Import Libraries
###################################################
# Standard Libraries
import datetime


# Third-Party Libraries

# Local Libraries

###################################################
# Date Utils
###################################################
def chunk_date_range(start_date: datetime.date, end_date: datetime.date) -> list:
    """
    Chunk the date range into at most 31-day intervals.

    @param start_date: The start date of the range.
    @param end_date: The end date of the range.
    @return: List of date ranges.
    """
    # Initialize the date range list
    date_range_list = []

    # Calculate the number of days between the start_date and end_date
    delta = (end_date - start_date).days + 1

    # Check if the delta is less than 31 days
    if delta <= 31:
        # Append the date range to the list
        date_range_list.append((start_date, end_date))
    else:
        # Initialize the current_date
        current_date = start_date

        # Iterate until the current_date is less than the end_date
        while current_date < end_date:
            # Calculate the new end_date
            new_end_date = current_date + datetime.timedelta(days=30)

            # Check if the new_end_date is greater than the end_date
            if new_end_date > end_date:
                # Set the new_end_date to the end_date
                new_end_date = end_date

            # Append the date range to the list
            date_range_list.append((current_date, new_end_date))

            # Update the current_date
            current_date = new_end_date + datetime.timedelta(days=1)

    return date_range_list
