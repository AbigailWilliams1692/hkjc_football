###################################################
# Project: HKJC Football
# Script: scraper/live_match_scraper.py
# Description: scraper class for match odds
# Author: AbigailWilliams
# Date: 2025-01-24
###################################################

###################################################
# Import Libraries
###################################################
# Standard Libraries
import os
from typing import Optional

# Third-Party Libraries

# Local Libraries
from v2.scraper.scraper_base import HKJC_Football_Scraper


###################################################
# Add root directory to the sys path
###################################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


###################################################
# Live Match Scraper Class
###################################################
class LiveMatchScraper(HKJC_Football_Scraper):
    """
    Live Match Scraper class
    """

    ##################################################
    # Constructor
    ##################################################
    def __init__(self) -> None:
        super().__init__()

    ##################################################
    # Get live and upcoming matches
    ##################################################
    def get_live_and_upcoming_matches_info(self) -> list[dict]:
        """
        Scrape the live and upcoming matches' info.

        @return: List containing the live and upcoming matches.
        """
        return self.get_live_matches_info_by_match_ids(match_id_list=None)

    ##################################################
    # Get live matches info by match IDs
    ##################################################
    def get_live_matches_info_by_match_ids(self, match_id_list: Optional[list[str]]) -> list[dict]:
        """
        Scrape the info for the live matches by the given match ID list.

        @param match_id_list: A list of matches' IDs to scrape odds for.
        @return: Dictionary containing the odds for the given matches.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template(f"{root_dir}/v2/graphql_query_templates/query_for_live_matches_template.txt")

        # Variables
        variables = {
            "fbOddsTypes": ["HAD", "EHA", "SGA", "CHP", "TQL", "FHA", "HHA", "HDC", "EDC", "HIL", "EHL", "FHL", "CHL",
                            "ECH", "FCH", "CRS", "ECS", "FCS", "FTS", "TTG", "ETG", "OOE", "FGS", "HFT", "MSP", "NTS",
                            "ENT", ],
            "fbOddsTypesM": ["HAD", "EHA", "SGA", "CHP", "TQL", "FHA", "HHA", "HDC", "EDC", "HIL", "EHL", "FHL", "CHL",
                             "ECH", "FCH", "CRS", "ECS", "FCS", "FTS", "TTG", "ETG", "OOE", "FGS", "HFT", "MSP", "NTS",
                             "ENT", ],
            "inplayOnly": False,
            "featuredMatchesOnly": False,
            "startDate": None,
            "endDate": None,
            "tournIds": None,
            "matchIds": match_id_list,
            "tournId": None,
            "tournProfileId": None,
            "subType": None,
            "startIndex": None,
            "endIndex": None,
            "frontEndIds": None,
            "earlySettlementOnly": False,
            "showAllMatch": False,
            "tday": None,
            "tIdList": None,
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

        return data["data"]["matches"]
