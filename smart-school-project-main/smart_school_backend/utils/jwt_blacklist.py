# smart_school_backend/utils/jwt_blacklist.py
"""
JWT Token Blacklist Manager

Provides functionality to blacklist tokens for logout.
Tokens are stored in memory with their expiration time.
"""

import logging
from datetime import datetime, timedelta
from typing import Set, Dict
import os

logger = logging.getLogger(__name__)

# In-memory blacklist storage
# For production, consider using Redis
_token_blacklist: Set[str] = {}
_token_expiry: Dict[str, datetime] = {}

# Default blacklist duration (24 hours matching JWT expiration)
BLACKLIST_DURATION_HOURS = int(os.getenv("JWT_BLACKLIST_DURATION_HOURS", "24"))

def add_to_blacklist(jti: str) -> bool:
    """
    Add a token to the blacklist.
    Returns True if added successfully.
    """
    _token_blacklist.add(jti)
    _token_expiry[jti] = datetime.utcnow() + timedelta(hours=BLACKLIST_DURATION_HOURS)
    logger.info(f"Token {jti} added to blacklist")
    return True

def is_blacklisted(jti: str) -> bool:
    """
    Check if a token is blacklisted.
    Automatically cleans up expired entries.
    """
    if jti not in _token_blacklist:
        return False
    
    # Check if expired
    if jti in _token_expiry:
        if datetime.utcnow() > _token_expiry[jti]:
            # Clean up expired entry
            _token_blacklist.discard(jti)
            _token_expiry.pop(jti, None)
            return False
    
    return True

def cleanup_expired():
    """
    Clean up all expired entries from the blacklist.
    Should be called periodically.
    """
    now = datetime.utcnow()
    expired = [jti for jti, expiry in _token_expiry.items() if now > expiry]
    
    for jti in expired:
        _token_blacklist.discard(jti)
        _token_expiry.pop(jti, None)
    
    if expired:
        logger.info(f"Cleaned up {len(expired)} expired tokens from blacklist")
    
    return len(expired)

def get_blacklist_count() -> int:
    """Get current count of blacklisted tokens"""
    return len(_token_blacklist)
