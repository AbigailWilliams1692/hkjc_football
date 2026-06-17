#######################################################################
# Project: Data Retrieval Module
# File: exceptions.py
# Description: Exception classes for HKJC Football data parsing
# Author: AbigailWilliams1692
# Created: 2026-06-17
# Updated: 2026-06-17
#######################################################################

#######################################################################
# Data Parsing Exceptions
#######################################################################
class DataParsingError(Exception):
    """Base exception for data parsing errors."""
    pass


class DataParsingKeyError(DataParsingError):
    """Exception raised when a required key is missing in the parsed data."""
    pass
