###################################################
# Project: HKJC Football
# Script: scraper/scraper_base.py
# Description: Base class for the HKJC Football Scraper
# Author: AbigailWilliams
# Date: 2025-01-04
###################################################

###################################################
# Import Libraries
###################################################
# Standard Libraries

# Third-Party Libraries

# Local Libraries
from v2.scraper.scraper_base import HKJC_Football_Scraper


###################################################
# Match Odds Scraper Class
###################################################
class MatchOddsScraper(HKJC_Football_Scraper):
    """
    Match Odds Scraper class
    """

    ##################################################
    # Constructor
    ##################################################
    def __init__(self) -> None:
        super().__init__()

    ##################################################
    # Core Methods
    ##################################################
    def get_odds_by_match_ids(self, match_ids: list) -> dict:
        """
        Scrape the match odds by the given match IDs.

        @param match_ids: A list of matches' IDs to scrape odds for.
        @return: Dictionary containing the odds for the given matches.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template_file("query_for_odds_template.txt")

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
            "matchIds": match_ids,
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

        return data
