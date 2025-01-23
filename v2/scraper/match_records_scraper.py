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
import os

# Third-Party Libraries

# Local Libraries
from v2.scraper.date_utils import chunk_date_range
from v2.scraper.scraper_base import HKJC_Football_Scraper


###################################################
# Add root directory to the sys path
###################################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


###################################################
# Match Results Scraper Class
###################################################
class MatchRecordsScraper(HKJC_Football_Scraper):
    """
    Match Results Scraper class
    """

    ##################################################
    # Constructor
    ##################################################
    def __init__(self) -> None:
        super().__init__()

    ##################################################
    # Get historical matches
    ##################################################
    def get_historical_matches(self,
                               start_date: datetime.date = None,
                               end_date: datetime.date = None,
                               team_id: str = None
                               ) -> list:
        """
        Scrape the match records by the given team_id, start_date, and end_date.
        **The start_date and end_date can be more than 31 days apart since this method with handle the date issue.**

        @param start_date: The start date to search matches for.
        @param end_date: The end date to search matches for.
        @param team_id: The team ID to search matches for.
        @return: List containing the results for the given matches.
        """
        # Chunk the date range
        date_ranges = chunk_date_range(start_date, end_date)

        # Initialize the container for the match results
        match_results_list: list[dict] = []

        # Get the match results for each date range
        for start_date, end_date in date_ranges:
            match_results = self.get_historical_matches_short_period(
                start_date=start_date,
                end_date=end_date,
                team_id=team_id,
            )
            match_results_list.extend(match_results)

        return match_results_list

    def get_historical_matches_short_period(self,
                                            start_date: datetime.date = None,
                                            end_date: datetime.date = None,
                                            team_id: str = None
                                            ) -> list:
        """
        Scrape the match records by the given team_id, start_date, and end_date.
        **The start_date and end_date can at most be 31 days apart**

        @param start_date: The start date to search matches for.
        @param end_date: The end date to search matches for.
        @param team_id: The team ID to search matches for.
        @return: List containing the results for the given matches.
        """
        # Initialize the container for the match results
        match_results_list: list[dict] = []

        # iteratively get the match results
        start_index, end_index = 1, 20
        while True:
            # Get the match results
            match_results_json = self.get_historical_matches_core(
                start_index=start_index,
                end_index=end_index,
                start_date=start_date,
                end_date=end_date,
                team_id=team_id,
            )

            # Append the match results to the container
            match_results_list.extend(
                match_results_json["data"]["matches"]
            )

            # Update the start index and end index
            start_index += 20
            end_index += 20

            # Break if the total number of matches is less than the end index
            total_number_of_matches = match_results_json["data"]["matchNumByDate"]["total"]
            if total_number_of_matches <= end_index:
                break

        return match_results_list

    def get_historical_matches_core(self,
                                    start_index: int,
                                    end_index: int,
                                    start_date: datetime.date = None,
                                    end_date: datetime.date = None,
                                    team_id: str = None
                                    ) -> dict:
        """
        Scrape the match records by the given team_id, start_date, end_date, start_index and end_index.
        **The start_index and end_index is passed on from the parent method**

        @param start_index: The start index to search matches for.
        @param end_index: The end index to search matches for.
        @param start_date: The start date to search matches for.
        @param end_date: The end date to search matches for.
        @param team_id: The team ID to search matches for.
        @return: List containing the results for the given matches.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template(
            f"{root_dir}/v2/graphql_query_templates/query_for_historical_matches_template.txt")

        # Variables
        variables = {
            "startDate": start_date.strftime("%Y-%m-%d") if start_date else None,
            "endDate": end_date.strftime("%Y-%m-%d") if end_date else None,
            "startIndex": start_index,
            "endIndex": end_index,
            "teamId": team_id,
        }

        # Payload
        payload = {
            "variables": variables,
            "query": graphql_template,
        }

        # Scrape
        data = self.post(
            url=self.graphql_url,
            headers=self.generate_headers(),
            payload=payload,
        )

        return data

    ##################################################
    # Get historical match results by match ID
    ##################################################
    def get_match_results_by_batch(self, match_id_list: list[str]) -> list:
        """
        Scrape the match results by the given list of match_id_list.

        @param match_id_list: The match ID list to search matches for.
        @return: List containing the results for the given matches.
        """
        # Initialize the container for the match results
        match_results_list: list[dict] = []

        # Get the match results for each match ID
        for match_id in match_id_list:
            match_result = self.get_match_result_by_match_id(
                match_id=match_id,
            )
            match_results_list.append(match_result)

        return match_results_list

    def get_match_result_by_match_id(self, match_id: str) -> dict:
        """
        Scrape the match results by the given match_id.

        @param match_id: The match ID to search matches for.
        @return: List containing the results for the given matches.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template(
            f"{root_dir}/v2/graphql_query_templates/query_for_historical_match_result_template.txt"
        )

        # Variables
        variables = {
            "matchId": match_id,
        }

        # Payload
        payload = {
            "variables": variables,
            "query": graphql_template,
        }

        # Scrape
        data = self.post(
            url=self.graphql_url,
            headers=self.generate_headers(),
            payload=payload,
        )

        return data["data"]["matches"][0]

    ##################################################
    # Get historical match odds by match ID
    ##################################################
    def get_match_odds_by_batch(self, match_id_list: list[str]) -> list:
        """
        Scrape the match odds by the given list of match_id_list.

        @param match_id_list: The match ID list to search matches for.
        @return: List containing the results for the given matches.
        """
        # Initialize the container for the match odds
        match_odds_list: list[dict] = []

        # Get the match odds for each match ID
        for match_id in match_id_list:
            match_odds = self.get_match_odds_by_match_id(
                match_id=match_id,
            )
            match_odds_list.append(match_odds)

        return match_odds_list

    def get_match_odds_by_match_id(self, match_id: str) -> dict:
        """
        Scrape the match odds by the given match_id.

        @param match_id: The match ID to search matches for.
        @return: List containing the results for the given matches.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template(
            f"{root_dir}/v2/graphql_query_templates/query_for_historical_match_odds_template.txt"
        )

        # Variables
        variables = {
            "matchId": match_id,
        }

        # Payload
        payload = {
            "variables": variables,
            "query": graphql_template,
        }

        # Scrape
        data = self.post(
            url=self.graphql_url,
            headers=self.generate_headers(),
            payload=payload,
        )

        return data["data"]["matches"][0]