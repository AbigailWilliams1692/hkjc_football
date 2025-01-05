###################################################
# Project: HKJC Football
# Script: scraper/team_id_scraper.py
# Description: scraper class for team IDs
# Author: AbigailWilliams
# Date: 2025-01-05
###################################################

###################################################
# Import Libraries
###################################################
# Standard Libraries
import os

# Third-Party Libraries

# Local Libraries
from v2.scraper.scraper_base import HKJC_Football_Scraper


###################################################
# Add root directory to the sys path
###################################################
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


###################################################
# Team ID Scraper Class
###################################################
class TeamIDScraper(HKJC_Football_Scraper):
    """
    Team ID Scraper class
    """

    ##################################################
    # Constructor
    ##################################################
    def __init__(self) -> None:
        super().__init__()

    ##################################################
    # Core Methods
    ##################################################
    def get_team_ids(self) -> dict:
        """
        Scrape the team IDs.

        @return: Dictionary containing the team IDs.
        """
        # Load the GraphQL template
        graphql_template = self.load_graphql_template(f"{root_dir}/v2/graphql_query_templates/query_for_team_ids_template.txt")

        # Variables
        variables = {}

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


if __name__ == "__main__":
    import pandas as pd
    team_id_scraper = TeamIDScraper()
    team_ids_data = team_id_scraper.get_team_ids()
    df = pd.DataFrame(team_ids_data["data"]["teamList"])
    print(df)
    print(df.id.dtype)
