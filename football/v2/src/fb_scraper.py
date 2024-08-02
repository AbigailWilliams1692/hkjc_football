###########################################
# Project: HKJC Scraper
# File: fb_scraper.py
# Author: Abigail Williams
# Date: 2024-08-02
###########################################

###########################################
# Import Packages
# Standard Packages
import json
import requests
from abc import abstractmethod

# Third-Party Packages

# Local Packages
from common.src.scraper import Scraper

###########################################

###########################################
# Scraper Class
class FootballBettingScraper(Scraper):
    """
    Football Betting Scraper class
    """

    # Class Attributes
    graphql_url = "https://info.cld.hkjc.com/graphql/base/"
    graphql_templates = {
        "query_for_odds": "query_for_odds_template.txt",
        "query_for_matches": "query_for_matches_template.txt",
    }
    
    # Constructor
    def __init__(self) -> None:
        super().__init__()
        pass
    
    # Core Methods
    def scrape(self, url: str, headers: dict, payload: dict) -> dict:
        """
        Scrape data from the given URL.

        @param url: URL to scrape data from.
        @param headers: Headers for the request.
        @param payload: Payload for the request.
        @return: JSON dictionary.
        """
        response = requests.post(
            url=url,
            headers=headers,
            data=payload
        )
        if response.status_code != 200:
            raise Exception(f"Failed to scrape data from the given URL. \n\tStatus Code: {response.status_code} \n\tResponse: {response.text}")
        else:
            return response.json()
    
    def save(self, data: dict, path: str, ) -> None:
        """
        Save the data to file.

        @param data: Data to save.
        @param path: Path to save the data.
        @return: None.
        """
        with open(path, "w") as f:
            json.dump(data, f)

    def load_graphql_template(self, template_name: str) -> str:
        """
        Load the given GraphQL template.

        @param template_name: Name of the template to load.
        @return: GraphQL template string.
        """
        graphql_template_path = f"football/v2/graphql_templates/{self.graphql_templates[template_name]}"
        with open(graphql_template_path, "r") as f:
            return f.read()
    
    # Scrape the odds for the given matches
    def scrape_odds_by_match_ids(self, match_ids: list) -> dict:
        """
        Scrape the odds by the given match IDs.

        @param match_ids: A list of matches's IDs to scrape odds for.
        @return: Dictionary containing the odds for the given matches.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template("query_for_odds")

        # Variables
        variables = {
            "fbOddsTypes": ["HAD", "EHA", "SGA", "CHP", "TQL", "FHA", "HHA", "HDC", "EDC", "HIL", "EHL", "FHL", "CHL", "ECH", "FCH", "CRS", "ECS", "FCS", "FTS", "TTG", "ETG", "OOE", "FGS", "HFT", "MSP", "NTS", "ENT",],
            "fbOddsTypesM": ["HAD", "EHA", "SGA", "CHP", "TQL", "FHA", "HHA", "HDC", "EDC", "HIL", "EHL", "FHL", "CHL", "ECH", "FCH", "CRS", "ECS", "FCS", "FTS", "TTG", "ETG", "OOE", "FGS", "HFT", "MSP", "NTS", "ENT",],
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
        data = self.scrape(
            url=self.graphql_url,
            headers=self.generate_headers(),
            payload=json.dumps(payload)
        )

        return data
