#######################################################################
# Project: HKJC Football
# File: hkjc_football_data_parser.py
# Description: HKJC Football Data Parser - to parse the data into
#              a standardized format that makes sense for downstream
#              processing.
# Author: AbigailWilliams
# Created: 2025-06-17
# Updated: 2026-06-17
#######################################################################

#######################################################################
# Import Packages
#######################################################################
# Standard Packages
import logging
from abc import ABC, abstractmethod
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
class HKJC_Football_DataParser(ABC, DataModule):
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
    # Abstract Methods
    #################################################
    @abstractmethod
    def parse(self, data: Any) -> Dict[str, Any] | List[Dict[str, Any]]:
        """
        Parse the data into a useful and standardized format.
        
        :param data: Raw data to parse.
        :return: Parsed data in standardized format.
        """
        raise NotImplementedError("Subclasses must implement parse method")
