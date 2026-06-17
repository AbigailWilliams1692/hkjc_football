#######################################################################
# Project: HKJC Football
# File: match_result_data_parser.py
# Description: Parse match result data.
# Author: AbigailWilliams
# Created: 2025-06-18
# Updated: 2026-06-18
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from abc import ABC
from tkinter import N
from typing import Any, Dict, List, Optional

# Third-Party Packages

# Local Packages
from .hkjc_football_data_parser import HKJC_Football_DataParser


#######################################################################
# Constants
#######################################################################


#######################################################################
# Match Result Data Parser
#######################################################################
class MatchResult_DataParser(ABC, HKJC_Football_DataParser):
    """
    Match Result Data Parser - to parse the match result data into
    a standardized format that makes sense for downstream
    processing.
    """
    
    #################################################
    # Class Attributes
    #################################################
    __name: str = "MatchResult_DataParser"
    __type: str = "DataParser"
    __score_time_period_map: Dict[str, str] = {"FT": "CRS", "HT": "FCS"}
    __first_team_to_score_map: Dict[str, str] = {"H": "Home", "A": "Away", "N": "No Goal"}

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
        **kwargs
    ):
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
            **kwargs
        )
    
    #################################################
    # Implement the abstract parse method
    #################################################
    def parse(self, data: Any) -> Dict[str, Any]:
        """
        Parse the data into a standardized format.
        
        Args:
            data: The data to parse
            
        Returns:
            Dict[str, Any]: The parsed data
        """
        pass
    
    #################################################
    # Utility methods
    #################################################
    @staticmethod
    def extract_pool_by_odd_type(pools: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract the pools and group them by odd type.
        
        :param pools: The list of pools to extract from
        :return: Dict[str, List[Dict[str, Any]]]: The extracted pools grouped by odd type
        """
        # Initialize a dictionary to store the pools grouped by odd type
        pools_by_odd_type = {}

        # Iterate through each pool
        for pool in pools:
            # Get the odd type of the pool
            pool_odd_type = pool.get("oddType", None)
            
            # Group the pools by odd type
            if pool_odd_type not in pools_by_odd_type:
                pools_by_odd_type[pool_odd_type] = []
            pools_by_odd_type[pool_odd_type].append(pool)
        
        return pools_by_odd_type

    # --- CRS / FCS: Correct score (波膽 / 半場波膽) ---
    def extract_score(self, pools_by_odd_type: Dict[str, List[Dict[str, Any]]], time_period: str) -> Dict[str, Any]:
        """
        Extract the correct score for the given time period.

        :param pools_by_odd_type: The pools grouped by odd type
        :param time_period: "FT" for full time (CRS pool) or "HT" for half time (FCS pool)
        :return: Dict[str, Any]: The correct score
        """
        # Validate the time period
        if time_period not in self.__score_time_period_map.keys():
            raise ValueError(f"Invalid time_period '{time_period}'. Expected 'FT' or 'HT'.")

        # Get the pool type for the given time period
        pool_type = self.__score_time_period_map[time_period]

        # Get the pool for the given time period
        pool = pools_by_odd_type.get(pool_type, [])

        if len(pool) > 0:

            # Find the winning combinations
            winning_combinations = self.extract_winning_combinations(pool=pool[0])

            if len(winning_combinations) == 1:

                # Extract the score
                score = self.parse_score_str(winning_combinations[0]["str"])

                # Formulate the return data
                data = {
                    "home": score.get("home", None),
                    "away": score.get("away", None),
                    "total": score.get("total", None),
                    "display": score.get("display", None),
                }

            elif len(winning_combinations) > 1:

                # Multiple winning combinations found, raise an exception to indicate this is unexpected.
                # The exception type is to be implemented in the future.
                raise Exception(f"Multiple winning combinations found in {pool_type} pool.")

            else:
                # No winning combinations found, return None
                raise Exception(f"No winning combinations found in {pool_type} pool.")

        else:
            # No pool found, raise exception
            raise Exception(f"No {pool_type} pool found.")

        return data

    def extract_first_team_to_score(self, pools_by_odd_type: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Extract the first team to score.
        
        :param pools_by_odd_type: The pools grouped by odd type
        :return: Dict[str, Any]: The first team to score
        """
        # Get the pool for the given time period
        pool = pools_by_odd_type.get("FTS", [])

        if len(pool) > 0:

            # Find the winning combinations
            winning_combinations = self.extract_winning_combinations(pool=pool[0])

            if len(winning_combinations) == 1:

                # Extract the team
                team = winning_combinations[0]["str"]

                # Formulate the return data
                data = {
                    "first_team_to_score": self.__first_team_to_score_map.get(team, team),
                }

            elif len(winning_combinations) > 1:

                # Multiple winning combinations found, raise an exception to indicate this is unexpected.
                # The exception type is to be implemented in the future.
                raise Exception("Multiple winning combinations found in 1ST TEAM TO SCORE pool.")

            else:
                # No winning combinations found, return None
                raise Exception("No winning combinations found in 1ST TEAM TO SCORE pool.")

        else:
            # No pool found, raise exception
            raise Exception("No 1ST TEAM TO SCORE pool found.")

        return data
        
    
    def extract_winning_combinations(self, pool: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract the winning combinations from a pool.
        
        :param pool: The pool to extract from
        :return: List[Dict[str, Any]]: The winning combinations
        """
        # Initialize a list container
        winning_combinations = []

        # Iterate through each line in the pool
        for line in pool.get("lines", []):

            # Get the combinations from the line
            combinations = line.get("combinations", [])

            # Extract the winning combination
            winner = self.extract_winning_combination(combinations)
            
            # Add the winning combination to the list if it exists
            if winner:
                winning_combinations.append(winner)

        return winning_combinations

    @staticmethod
    def extract_winning_combination(combinations: List[Dict]) -> Dict[str, Any]:
        """
        Extract the winning combination from a list of combinations.

        :param combinations: The list of combinations to extract from
        :return: Dict[str, Any]: The winning combination
        """
        # Iterate through each combination
        for combination in combinations:

            # Get the status of the combination
            status = combination.get("status", None)
            
            # Check if the combination is a winner; if so, return a dictionary with the relevant fields
            if status == "WIN":
                return {
                    "str": combination.get("str"),
                    "status": status,
                    "winOrd": combination.get("winOrd"),
                    "name_en": combination.get("name_en", ""),
                    "name_ch": combination.get("name_ch", ""),
                    "selections": combination.get("selections", []),
                }

        return {}    
            
    @staticmethod
    def parse_score_str(score_str: str) -> Optional[Dict[str, int]]:
        """
        Parse '04:02' or '2:1' like strings into home/away goals. Returns None if not parsable.
        
        :param score_str: The score string to parse
        :return: Optional[Dict[str, int]]: The parsed score or None if not parsable
        """
        # Force validate the type of score_str
        if not isinstance(score_str, str):
            raise TypeError(f"Expected str, got {type(score_str).__name__} when parsing score string: {score_str}")
        # Check if the string is empty or doesn't contain a colon
        elif len(score_str) == 0 or ":" not in score_str:
            raise ValueError(f"Invalid score string: {score_str}")
        
        # Parse the score_str
        parts = score_str.split(":")
        if len(parts) == 2:
            home_score = int(parts[0])
            away_score = int(parts[1])
            return {
                "home": home_score,
                "away": away_score,
                "display": f"{home_score}-{away_score}"
            }
        else:
            raise ValueError(f"Invalid score string: {score_str}")
