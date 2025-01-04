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
import requests


# Third-Party Libraries

###################################################
# Scraper Base Class
###################################################
class HKJC_Football_Scraper(object):
    """
    Base class for the HKJC Football Scraper
    """

    ##################################################
    # Class Attributes
    ##################################################
    graphql_url = "https://info.cld.hkjc.com/graphql/base"
    graphql_templates_root_dir = "v2/graphql_templates"

    ##################################################
    # Constructor
    ##################################################
    def __init__(self) -> None:
        pass

    ##################################################
    # Core Methods
    ##################################################
    @staticmethod
    def generate_headers() -> dict:
        """
        Generate headers for the request.
        """
        return {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

    @staticmethod
    def get() -> dict:
        """
        Get data from the given URL.
        """
        pass

    @staticmethod
    def post(url: str, headers: dict, payload: dict) -> dict:
        """
        Post the data to the given URL.

        @param url: URL to scrape data from.
        @param headers: Headers for the request.
        @param payload: Payload for the request.
        @return: JSON dictionary.
        """
        # post the request
        response = requests.post(
            url=url,
            headers=headers,
            data=payload,
        )

        # check if the response is successful
        if response.status_code != 200:
            raise Exception(
                f"Failed to scrape data from the given URL. \n\tStatus Code: {response.status_code} \n\tResponse: {response.text}")
        else:
            return response.json()

    def load_graphql_template_file(self, template_filename: str) -> str:
        """
        Load the given GraphQL template.

        @param template_filename: the filename of the template.
        @return: GraphQL template string.
        """
        # write a function for me

        graphql_template_path = f"{self.graphql_templates_root_dir}/{template_filename}"
        with open(graphql_template_path, "r") as f:
            return f.read()
