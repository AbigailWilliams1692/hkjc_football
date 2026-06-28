#######################################################################
# Project: HKJC Football
# File: hkjc_football_data_provider.py
# Description: HKJC Football Data Provider – a single data provider
#              class that consolidates the various scraper classes
#              (TeamIDScraper, LiveMatchScraper, MatchRecordsScraper)
#              into one unified RestAPI_DataProvider subclass.
# Author: AbigailWilliams
# Created: 2025-01-04
# Updated: 2026-06-28
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import datetime
import json
import logging
import os
from typing import Any, Dict, List, Optional

# Third-Party Packages

# Local Packages
from data_retrieval import RestAPI_DataProvider
from hkjc_core.utils.date_utils import chunk_date_range


#######################################################################
# Constants
#######################################################################
# Config Directory
_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

# GraphQL Templates Directory
_GRAPHQL_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "graphql_templates")

# HKJC GraphQL Base URL
HKJC_GRAPHQL_BASE_URL = "https://info.cld.hkjc.com/graphql/base/"


#######################################################################
# HKJC Football Data Provider
#######################################################################
class HKJC_Football_DataProvider(RestAPI_DataProvider):
    """
    Unified HKJC Football data provider.

    Consolidates the functionality previously spread across
    TeamIDScraper, LiveMatchScraper, and MatchRecordsScraper into a
    single RestAPI_DataProvider subclass.

    Supported data points (via ``fetch_data``):
        - ``"team_ids"``             → get_team_ids()
        - ``"live_matches"``         → get_live_matches_info(...)
        - ``"historical_matches"``   → get_historical_matches(...)
        - ``"match_result"``         → get_match_result_by_match_id(...)
        - ``"match_results_batch"``  → get_match_results_by_batch(...)
        - ``"match_odds"``           → get_match_odds_by_match_id(...)
        - ``"match_odds_batch"``     → get_match_odds_by_batch(...)
    """

    ###################################################################
    # Class Attributes
    ###################################################################
    __name = "HKJC_Football_DataProvider"
    __type = "HKJC_Football_DataProvider"

    ###################################################################
    # Constructor
    ###################################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.3,
        **config,
    ) -> None:
        """
        Initialize the HKJC Football Data Provider.

        :param instance_id: Unique identifier for this provider instance.
        :param logger: Logger instance for logging operations.
        :param log_level: Logging level for the data provider.
        :param base_url: Base URL for the HKJC GraphQL API.
        :param timeout: Request timeout in seconds.
        :param max_retries: Maximum number of retry attempts.
        :param retry_backoff_factor: Backoff factor for retry delays.
        :param config: Additional configuration parameters.
        """
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
            base_url=base_url or HKJC_GRAPHQL_BASE_URL,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
            **config,
        )

        # Ensure get_base_url() returns the correct value
        self.set_base_url(base_url=base_url or HKJC_GRAPHQL_BASE_URL)

        # Pre-load football odds types
        self._football_odds_types: List[str] = self._load_football_odd_types()

        # Pre-load GraphQL query templates
        self._graphql_templates: Dict[str, str] = self._load_all_graphql_templates()

        # Register data methods so they can be invoked via fetch_data()
        self.update_data_methods(
            {
                "team_ids":                     self.get_team_ids,
                "live_matches":                 self.get_live_matches,
                "all_live_matches":             self.get_all_live_matches,
                "match_results":                self.get_match_results,
                "match_result_details":         self.get_match_result_details,
                "match_result_details_in_batch":self.get_match_result_details_in_batch,
                "match_odds":                   self.get_match_odds,
                "match_odds_in_batch":          self.get_match_odds_in_batch,
            }
        )

    ###################################################################
    # Football Odds Types
    ###################################################################
    @staticmethod
    def _load_football_odd_types() -> List[str]:
        """
        Load football odd types from the odd_types directory.

        :return: List of football odd types.
        """
        # Default Football Odds Types loaded from config
        with open(os.path.join(_CONFIG_DIR, "default_fb_odds_types.json"), "r") as _f:
            deault_fb_odds_types: List[str] = json.load(_f)
        return deault_fb_odds_types

    def _get_default_odds_types(self) -> List[str]:
        """
        Get the list of football odds types.

        :return: List of football odds types.
        """
        return self._football_odds_types

    ###################################################################
    # GraphQL Template Helpers
    ###################################################################
    @staticmethod
    def _load_graphql_template(template_filename: str) -> str:
        """
        Load a GraphQL query template from the templates directory.

        :param template_filename: Filename of the template (relative to
            the ``graphql_templates`` directory).
        :return: The template string.
        """
        file_path = os.path.join(_GRAPHQL_TEMPLATES_DIR, template_filename)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_all_graphql_templates(self) -> Dict[str, str]:
        """
        Pre-load all GraphQL templates into a dictionary.

        :return: Dictionary mapping logical names to template strings.
        """
        return {
            "team_ids":             self._load_graphql_template("query_for_team_ids_template.graphql"),
            "live_matches":         self._load_graphql_template("query_for_live_matches_template.graphql"),
            "all_live_matches":     self._load_graphql_template("query_for_all_live_matches_template.graphql"),
            "match_results":        self._load_graphql_template("query_for_historical_match_results_template.graphql"),
            "match_result_details": self._load_graphql_template("query_for_historical_match_result_details_template.graphql"),
            "match_odds":           self._load_graphql_template("query_for_historical_match_odds_template.graphql"),
        }

    def _get_graphql_template(self, template_key: str) -> str:
        """
        Get a GraphQL template by key.

        :param template_key: Key identifying the template in
            ``self._graphql_templates``.
        :return: The template string.
        """
        if template_key not in self._graphql_templates:
            raise KeyError(f"Template key '{template_key}' not found in pre-loaded templates.")
        return self._graphql_templates[template_key]

    ###################################################################
    # Internal: POST a GraphQL query
    ###################################################################
    def _graphql_post(self, template_key: str, variables: Dict[str, Any], *args, **kwargs) -> Dict:
        """
        Execute a GraphQL POST request using a pre-loaded template.

        :param template_key: Key identifying the template in
            ``self._graphql_templates``.
        :param variables: GraphQL variables dictionary.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments, including operation_name.
        :return: Parsed JSON response dictionary.
        """
        # Define the payload for the GraphQL request
        # Note: trailing slash is required by the HKJC server (returns 403 without it)
        url = self.get_base_url() + "/"
        headers = self.generate_headers()
        payload = {
            "operationName": kwargs.get("operation_name"),
            "query": self._get_graphql_template(template_key=template_key),
            "variables": variables,
        }

        # Delete the operation_name if it's None
        if payload["operationName"] is None:
            del payload["operationName"]

        # Make the request
        return self._make_request(
            method="POST",
            url=url,
            headers=headers,
            json=payload,
        )

    ###################################################################
    # Data Method: Team IDs
    ###################################################################
    def get_team_ids(self) -> Dict:
        """
        Retrieve the full team list (IDs, codes, names).

        :return: Dictionary containing the team list response.
        """
        data = self._graphql_post(
            operation_name="teamList",
            template_key="team_ids",
            variables={},
        )
        return data.get("data", {}).get("teamList", [])

    ###################################################################
    # Data Methods: Live / Upcoming Match List
    ###################################################################
    def get_all_live_matches(self)-> List[Dict]:
        """
        Retrieve all live matches.
        
        :return: List of match info dictionaries.
        """
        data = self._graphql_post(template_key="all_live_matches", variables={})
        return data.get("data", {}).get("matches", [])

    def get_live_matches(
        self,
        match_id_list: Optional[List[str]] = None,
        in_play_only: bool = False,
        featured_matches_only: bool = False,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        tournament_id_list: Optional[List[str]] = None,
        tournament_id: Optional[str] = None,
        tournament_profile_id: Optional[str] = None,
        sub_type: Optional[str] = None,
        start_index: Optional[int] = None,
        end_index: Optional[int] = None,
        front_end_ids: Optional[List[str]] = None,
        early_settlement_only: bool = False,
        show_all_match: bool = False,
        tday: Optional[str] = None,
        t_id_list: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Retrieve live / upcoming match info, optionally filtered by match IDs.

        :param match_id_list: Optional list of match IDs to filter.
        :param in_play_only: If True, only return matches that are currently in play.
        :param featured_matches_only: If True, only return featured matches.
        :param start_date: Optional start date for filtering matches.
        :param end_date: Optional end date for filtering matches.
        :param tournament_id_list: Optional list of tournament IDs to filter.
        :param tournament_id: Optional single tournament ID to filter.
        :param tournament_profile_id: Optional tournament profile ID to filter.
        :param sub_type: Optional sub-type filter.
        :param start_index: Optional start index for pagination.
        :param end_index: Optional end index for pagination.
        :param front_end_ids: Optional list of front-end IDs to filter.
        :param early_settlement_only: If True, only return matches with early settlement.
        :param show_all_match: If True, show all matches regardless of other filters.
        :param tday: Optional date string for filtering.
        :param t_id_list: Optional list of tournament IDs to filter.
        :return: List of match info dictionaries.
        """
        variables = {
            "matchIds": match_id_list,
            "fbOddsTypes": self._get_default_odds_types(),
            "fbOddsTypesM": self._get_default_odds_types(),
            "inplayOnly": in_play_only,
            "featuredMatchesOnly": featured_matches_only,
            "startDate": start_date,
            "endDate": end_date,
            "tournIds": tournament_id_list,
            "tournId": tournament_id,
            "tournProfileId": tournament_profile_id,
            "subType": sub_type,
            "startIndex": start_index,
            "endIndex": end_index,
            "frontEndIds": front_end_ids,
            "earlySettlementOnly": early_settlement_only,
            "showAllMatch": show_all_match,
            "tday": tday,
            "tIdList": t_id_list,
        }
        data = self._graphql_post(template_key="live_matches", variables=variables)
        return data.get("data", {}).get("matches", [])

    ###################################################################
    # Data Methods: Match Results
    ###################################################################
    def get_match_results(
        self,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        team_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieve historical match results. Can handle date ranges > 31 days
        by automatically chunking the request period.

        :param start_date: Start date for the search window.
        :param end_date: End date for the search window.
        :param team_id: Optional team ID filter.
        :return: List of match record dictionaries.
        """
        # Chunk the date range into ≤ 31-day windows
        date_ranges = chunk_date_range(start_date=start_date, end_date=end_date)

        # Create container for the match records
        match_results_list: List[Dict] = []
        for chunk_start, chunk_end in date_ranges:
            matches = self._get_match_results_short_period(
                start_date=chunk_start,
                end_date=chunk_end,
                team_id=team_id,
            )
            match_results_list.extend(matches)

        return match_results_list

    def _get_match_results_short_period(
        self,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        team_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieve historical match results for a period of at most 31 days,
        paginating through all available results.

        :param start_date: Start date (max 31 days from end_date).
        :param end_date: End date.
        :param team_id: Optional team ID filter.
        :return: List of match record dictionaries.
        """
        # Create container for the match records
        match_results_list: List[Dict] = []

        # Set the default start_index and end_index
        start_index, end_index = 1, 20

        # Loop through all pages
        while True:
            
            # Retrieve the current page of match results
            data = self._get_match_results_page(
                start_index=start_index,
                end_index=end_index,
                start_date=start_date,
                end_date=end_date,
                team_id=team_id,
            )

            # Extend the match results list with the current page of match results
            match_results_list.extend(
                data.get("data", {}).get("matches", [])
            )

            # Check if we have fetched all match results
            total = data.get("data", {}).get("matchNumByDate", {}).get("total", 0)
            if total <= end_index:
                break

            # Increment the start and end indices for the next page
            start_index += 20
            end_index += 20

        return match_results_list
    
    def _get_match_results_page(
        self,
        start_index: int,
        end_index: int,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        team_id: Optional[str] = None,
    ) -> Dict:
        """
        Retrieve a single page of historical match results.

        :param start_index: Pagination start index.
        :param end_index: Pagination end index.
        :param start_date: Start date filter.
        :param end_date: End date filter.
        :param team_id: Optional team ID filter.
        :return: Raw JSON response dictionary.
        """
        variables = {
            "startDate": start_date.strftime("%Y-%m-%d") if start_date else None,
            "endDate": end_date.strftime("%Y-%m-%d") if end_date else None,
            "startIndex": start_index,
            "endIndex": end_index,
            "teamId": team_id,
        }
        return self._graphql_post(
            template_key="match_results", 
            variables=variables
        )

    ###################################################################
    # Data Methods: Match Result Details by Match ID
    ###################################################################
    def get_match_result_details_in_batch(self, match_id_list: List[str]) -> List[Dict]:
        """
        Retrieve match result details for a batch of match IDs.

        :param match_id_list: List of match IDs.
        :return: List of match result dictionaries.
        """
        match_results_list: List[Dict] = []
        for match_id in match_id_list:
            match_result = self.get_match_result_details(match_id=match_id)
            match_results_list.append(match_result)
        return match_results_list

    def get_match_result_details(self, match_id: str) -> Dict:
        """
        Retrieve match result details for a single match.

        :param match_id: The match ID.
        :return: Match result dictionary.
        """
        variables = {
            "matchId": match_id,
            "fbOddsTypes": self._get_default_odds_types(),
        }
        data = self._graphql_post(
            operation_name="matchResultDetails",
            template_key="match_result", 
            variables=variables
        )
        return data.get("data", {}).get("matches", [{}])[0]

    ###################################################################
    # Data Methods: Match Odds by Match ID
    ###################################################################
    def get_match_odds_in_batch(self, match_id_list: List[str]) -> List[Dict]:
        """
        Retrieve match odds for a batch of match IDs.

        :param match_id_list: List of match IDs.
        :return: List of match odds dictionaries.
        """
        match_odds_list: List[Dict] = []
        for match_id in match_id_list:
            match_odds = self.get_match_odds(match_id=match_id)
            match_odds_list.append(match_odds)
        return match_odds_list

    def get_match_odds(self, match_id: str) -> Dict:
        """
        Retrieve last odds for a single match.

        :param match_id: The match ID.
        :return: Match odds dictionary.
        """
        variables = {
            "matchId": match_id,
            "fbOddsTypes": self._get_default_odds_types(),
        }
        data = self._graphql_post(
            operation_name="lastOdds",
            template_key="match_odds", 
            variables=variables
        )
        return data.get("data", {}).get("matches", [{}])[0]
