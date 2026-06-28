#######################################################################
# Project: HKJC Football
# File: hkjc_football_data_parser.py
# Description: HKJC Football Data Parser - to parse the data into
#              a standardized format that makes sense for downstream
#              processing.
# Author: AbigailWilliams
# Created: 2025-06-17
# Updated: 2026-06-28
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import datetime
import logging
from typing import Any, Dict, List, Optional

# Third-Party Packages

# Local Packages
from data_retrieval import DataModule


#######################################################################
# Constants
#######################################################################


#######################################################################
# HKJC Football Data Parser
#######################################################################
class HKJC_Football_DataParser(DataModule):
    """
    HKJC Football Data Parser - to parse the data into
    a standardized format that makes sense for downstream
    processing.
    """

    #################################################
    # Class Attributes
    #################################################
    __name: str = "HKJC_Football_DataParser"
    __type: str = "DataParser"
    __score_time_period_map: Dict[str, str] = {"FT": "CRS", "HT": "FCS"}
    __first_team_to_score_map: Dict[str, str] = {"H": "Home", "A": "Away", "N": "No Goal"}
    __results_stage_id_map: Dict[str, int] = {"HT": 3, "FT": 5, "ET": 9, "ABD": 100}

    #################################################
    # Constructor
    #################################################
    def __init__(
        self,
        instance_id: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = logging.INFO,
    ) -> None:
        """
        Constructor for HKJC_Football_DataParser
        
        :param instance_id: Optional instance ID for tracking
        :param logger: Optional logger instance
        :param log_level: Logging level (default: INFO)
        """
        super().__init__(
            instance_id=instance_id,
            logger=logger,
            log_level=log_level,
        )

    #################################################
    # Entry Methods
    #################################################
    def parse_match_result(self, match_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the match result query response. Extract both the goals, corners and pools.
        
        :param match_result: The match result query response
        :return: Dict[str, Any]: The parsed match result
        """
        # Extract the match meta data
        match_id = match_result.get("id", "")
        front_end_id = match_result.get("frontEndId", "")
        kick_off_time = datetime.datetime.fromisoformat(match_result.get("kickOffTime", ""))
        tournament_info = self._extract_tournament_info(tournament_info=match_result.get("tournament", {}))
        home_team_info = self._extract_team_info(team_info=match_result.get("homeTeam", {}), home_or_away="home")
        away_team_info = self._extract_team_info(team_info=match_result.get("awayTeam", {}), home_or_away="away")

        # Extract the goals and corners
        match_result_list = match_result.get("results", [])
        ht_goals = self._extract_goals(match_result_list=match_result_list, time_period="HT")
        ft_goals = self._extract_goals(match_result_list=match_result_list, time_period="FT")
        ht_corners = self._extract_corners(match_result_list=match_result_list, time_period="HT")
        ft_corners = self._extract_corners(match_result_list=match_result_list, time_period="FT")
        
        # Extract the pools
        pool_info = match_result.get("poolInfo", "")
        defined_pools: List[str] = pool_info.get("definedPools", [])
        refund_pools: List[str] = pool_info.get("refundPools", [])
        payout_refund_pools: List[str] = pool_info.get("payoutRefundPools", [])
        
        # Extracted data
        extracted_data = {
            "match_id": match_id,
            "front_end_id": front_end_id,
            "kick_off_time": kick_off_time,
            "defined_pools": defined_pools,
            "refund_pools": refund_pools,
            "payout_refund_pools": payout_refund_pools,
        }
        extracted_data.update(tournament_info)
        extracted_data.update(home_team_info)
        extracted_data.update(away_team_info)
        extracted_data.update(ht_goals)
        extracted_data.update(ft_goals)
        extracted_data.update(ht_corners)
        extracted_data.update(ft_corners)

        return extracted_data

    def parse_match_odds(self, match_odds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the match odds query response. Return a flattened list of odds records,
        one record per combination, with match/pool/line metadata attached.

        :param match_odds: The match odds query response
        :return: List[Dict[str, Any]]: The flattened odds records
        """
        # Extract the match meta data
        match_id = match_odds.get("id", "")
        update_at = match_odds.get("updateAt", "")
        updated_at = datetime.datetime.fromisoformat(update_at) if update_at else None

        # Extract the odds records
        fo_pools = match_odds.get("foPools", [])
        odds_records = self._extract_odds_records(
            fo_pools=fo_pools,
            match_id=match_id,
            updated_at=updated_at,
        )

        return odds_records

    #################################################
    # Parse Match Result query response
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
            pool_odd_type = pool.get("oddsType", None)
            
            # Group the pools by odd type
            if pool_odd_type not in pools_by_odd_type:
                pools_by_odd_type[pool_odd_type] = []
            pools_by_odd_type[pool_odd_type].append(pool)
        
        return pools_by_odd_type

    #################################################
    # Parse Match Result - Home & Away Teams
    #################################################
    @staticmethod
    def _extract_team_info(team_info: Dict[str, Any], home_or_away: str) -> Dict[str, str]:
        """
        Extract team information from the team info dict.
        
        :param team_info: The team info dict to extract from
        :param home_or_away: The home or away team
        :return: Dict[str, str]: The extracted team information
        """
        if team_info == {}:
            return {}
        return {
            f"{home_or_away}_team_id": team_info.get("id", ""),
            f"{home_or_away}_team_name_en": team_info.get("name_en", ""),
            f"{home_or_away}_team_name_ch": team_info.get("name_ch", ""),
        }

    @staticmethod
    def _extract_tournament_info(tournament_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract tournament information from the tournament info dict.
        
        :param tournament_info: The tournament info dict to extract from
        :return: Dict[str, str]: The extracted tournament information
        """
        if tournament_info == {}:
            return {}
        return {
            "tournament_code": tournament_info.get("code", ""),
            "tournament_name_en": tournament_info.get("name_en", ""),
            "tournament_name_ch": tournament_info.get("name_ch", ""),
        }

    #################################################
    # Parse Match Result - Goals & Corners
    #################################################
    @staticmethod
    def _extract_result_entry(
        match_result_list: List[Dict[str, Any]],
        result_type: int,
        stage_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Extract the authoritative result entry for a given resultType and stageId.
        Replicates the JS Yh/Kh logic: filter by resultType, stageId,
        resultConfirmType > 1, payoutConfirmed == True, then take the entry
        with the highest sequence.

        :param match_result_list: The match 'results' list from the matchResults GraphQL response
        :param result_type: 1 = goals, 2 = corners
        :param stage_id: 3 = HT, 5 = FT, 9 = ET, 100 = abandoned
        :return: The matching result entry dict, or None if not found
        """
        candidates = [
            r for r in match_result_list
            if r.get("resultType") == result_type
            and r.get("stageId") == stage_id
            and r.get("resultConfirmType", 0) > 1
            and r.get("payoutConfirmed", False)
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r.get("sequence", 0))

    def _extract_goals(
        self,
        match_result_list: List[Dict[str, Any]],
        time_period: str,
    ) -> Dict[str, Any]:
        """
        Extract goals from the match 'results' list (matchResults query).

        :param match_result_list: The match 'results' list
        :param time_period: "FT" (stageId=5), "HT" (stageId=3), or "ET" (stageId=9)
        :return: Dict with home, away, total, display — or raises if not found
        """
        # Check input parameters
        if match_result_list == []:
            raise ValueError("match_result_list is empty")
        if time_period not in self.__results_stage_id_map:
            raise ValueError(f"Invalid time_period '{time_period}'. Expected one of {list(self.__results_stage_id_map.keys())}.")
        
        # Get the stage ID for the given time period
        stage_id = self.__results_stage_id_map[time_period]

        # Extract the result entry
        entry = self._extract_result_entry(
            match_result_list=match_result_list, result_type=1, stage_id=stage_id
        )

        # Check if the result entry is found
        if entry is None:
            self.get_logger().warning(f"No goals result found for {time_period} (stageId={stage_id}).")
            self.get_logger().warning(f"match_result_list: {match_result_list}")
            return {}
        
        # Extract the home and away goals
        home_goals = entry["homeResult"]
        away_goals = entry["awayResult"]
        
        return {
            f"{time_period}_home_goals": home_goals,
            f"{time_period}_away_goals": away_goals,
            f"{time_period}_total_goals": home_goals + away_goals,
        }

    def _extract_corners(
        self,
        match_result_list: List[Dict[str, Any]],
        time_period: str,
    ) -> Dict[str, Any]:
        """
        Extract corners from the match 'results' list (matchResults query).
        If ttlCornerResult != -1, uses it as total; otherwise sums homeResult + awayResult.

        :param match_result_list: The match 'results' list
        :param time_period: "FT" (stageId=5), "HT" (stageId=3), or "ET" (stageId=9)
        :return: Dict with home, away, total, display — or raises if not found
        """
        # Check input parameters
        if match_result_list == []:
            raise ValueError("match_result_list is empty")
        if time_period not in self.__results_stage_id_map:
            raise ValueError(f"Invalid time_period '{time_period}'. Expected one of {list(self.__results_stage_id_map.keys())}.")
        
        # Get the stage ID for the given time period
        stage_id = self.__results_stage_id_map[time_period]
        
        # Extract the result entry
        entry = self._extract_result_entry(
            match_result_list=match_result_list, result_type=2, stage_id=stage_id
        )

        # Check if the result entry is found
        if entry is None:
            self.get_logger().warning(f"No corners result found for {time_period} (stageId={stage_id}).")
            self.get_logger().warning(f"match_result_list: {match_result_list}")
            return {}
        
        # Extract the home and away corners
        home_corners = entry["homeResult"]
        away_corners = entry["awayResult"]
        ttl = entry.get("ttlCornerResult", -1)
        total_corners = ttl if ttl != -1 else home_corners + away_corners
        
        return {
            f"{time_period}_home_corners": home_corners,
            f"{time_period}_away_corners": away_corners,
            f"{time_period}_total_corners": total_corners,
        }

    #################################################
    # Parse Match Odds query response
    #################################################
    def _extract_odds_records(
        self,
        fo_pools: List[Dict[str, Any]],
        match_id: str = "",
        updated_at: Optional[datetime.datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract all odds records from the foPools list.
        Flattens pools, lines, and combinations into a list of records.
        "lines" are pre-play odds, "closedLines" are in-play odds.

        :param fo_pools: The list of pools from the match odds query response
        :param match_id: The match ID to include in each record
        :param updated_at: The match-level update timestamp to include in each record
        :return: List[Dict[str, Any]]: The flattened odds records
        """
        # Initialize a list container
        odds_records: List[Dict[str, Any]] = []

        # Iterate through each pool
        for pool in fo_pools:
            # Get the pool metadata
            pool_id = pool.get("id", "")
            pool_status = pool.get("status", "")
            odds_type = pool.get("oddsType", "")
            inst_no = pool.get("instNo", 0)
            inplay = pool.get("inplay", False)

            # Extract records from open lines
            for line in pool.get("lines", []):
                odds_records.extend(
                    self._extract_odds_record(
                        pool_id=pool_id,
                        pool_status=pool_status,
                        odds_type=odds_type,
                        inst_no=inst_no,
                        inplay=inplay,
                        line=line,
                        line_type="in-play",
                        match_id=match_id,
                        updated_at=updated_at,
                    )
                )

            # Extract records from closed lines
            for line in pool.get("closedLines", []):
                odds_records.extend(
                    self._extract_odds_record(
                        pool_id=pool_id,
                        pool_status=pool_status,
                        odds_type=odds_type,
                        inst_no=inst_no,
                        inplay=inplay,
                        line=line,
                        line_type="pre-play",
                        match_id=match_id,
                        updated_at=updated_at,
                    )
                )

        return odds_records

    def _extract_odds_record(
        self,
        pool_id: str,
        pool_status: str,
        odds_type: str,
        inst_no: int,
        inplay: bool,
        line: Dict[str, Any],
        line_type: str,
        match_id: str = "",
        updated_at: Optional[datetime.datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract odds records from a single line's combinations.

        :param pool_id: The pool ID
        :param pool_status: The pool status
        :param odds_type: The odds type
        :param inst_no: The instance number
        :param inplay: Whether the pool is inplay
        :param line: The line dict containing combinations
        :param line_type: "open" or "closed"
        :param match_id: The match ID
        :param updated_at: The match-level update timestamp
        :return: List[Dict[str, Any]]: The odds records for this line
        """
        # Initialize a list container
        records: List[Dict[str, Any]] = []

        # Get the line metadata
        line_id = line.get("lineId", "")
        line_status = line.get("status", "")
        condition = line.get("condition", "")

        # Iterate through each combination
        for combination in line.get("combinations", []):
            # Get the combination metadata
            comb_id = combination.get("combId", "")
            comb_str = combination.get("str", "")
            comb_status = combination.get("status", "")
            current_odds = combination.get("currentOdds", "")

            # Get the first selection (if available)
            selections = combination.get("selections", [])
            selection = selections[0] if selections else {}

            # Build the record
            record = {
                "match_id": match_id,
                "updated_at": updated_at,
                "odds_type": odds_type,
                "pool_id": pool_id,
                "pool_status": pool_status,
                "inst_no": inst_no,
                "inplay": inplay,
                "line_type": line_type,
                "line_id": line_id,
                "line_status": line_status,
                "condition": condition,
                "comb_id": comb_id,
                "comb_str": comb_str,
                "comb_status": comb_status,
                "current_odds": self._parse_odds_value(current_odds),
                "selection_str": selection.get("str", ""),
                "selection_name_en": selection.get("name_en", ""),
                "selection_name_ch": selection.get("name_ch", ""),
            }
            records.append(record)

        return records

    @staticmethod
    def _parse_odds_value(odds_str: str) -> Optional[float]:
        """
        Parse an odds string into a float.

        :param odds_str: The odds string to parse
        :return: Optional[float]: The parsed odds value, or None if not parsable
        """
        try:
            return float(odds_str)
        except (ValueError, TypeError):
            return None
