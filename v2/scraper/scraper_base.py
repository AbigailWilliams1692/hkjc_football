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
import os
import sys
import requests

# Third-Party Libraries


###################################################
# Set the path to the root directory
###################################################
sys.path.append("../../..")


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
    graphql_url = "https://info.cld.hkjc.com/graphql/base/"

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
            json=payload,
        )

        # check if the response is successful
        if response.status_code != 200:
            raise Exception(
                f"Failed to scrape data from the given URL. \n\tStatus Code: {response.status_code} \n\tResponse: {response.text}")
        else:
            return response.json()
