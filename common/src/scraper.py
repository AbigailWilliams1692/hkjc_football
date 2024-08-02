###########################################
# Project: HKJC Scraper
# File: scraper.py
# Author: Abigail Williams
# Date: 2024-08-02
###########################################

###########################################
# Import Packages
# Standard Packages
from abc import abstractmethod

# Third-Party Packages

# Local Packages

###########################################

###########################################
# Scraper Class
class Scraper(object):
    """
    Scraper base class
    """
    
    # Constructor
    def __init__(self) -> None:
        pass
    
    # Core Methods
    @abstractmethod
    def scrape(self) -> dict:
        """
        Abstract method to scrape data from a source. The return value should be a JSON dictionary. 
        """
        pass
    
    @abstractmethod
    def save(self, path: str, **params) -> None:
        """
        Save the data to file/DB.
        """
        pass
    
    @staticmethod
    def generate_headers() -> dict:
        """
        Generate headers for the request.
        """
        return {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

###########################################
