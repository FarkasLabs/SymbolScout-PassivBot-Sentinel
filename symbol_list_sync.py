import requests
from typing import Tuple, Set, Optional
from logger import logger


def fetch_symbolscout_list(endpoint: str) -> Optional[Set[str]]:
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        return set(data.get("symbols", []))
    except Exception as e:
        logger.error(f"Error fetching SymbolScout watchlist: {str(e)}")
        return None


def fetch_remotepairlist(endpoint: str) -> Optional[Set[str]]:
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()

        symbols = set()
        pairs = data.get("pairs", [])
        

        for pair in pairs:
            # Handle both formats: "BTC/USDT" and "BTC/USDT:USDT"
            base = pair.split("/")[0]
            symbols.add(base)

        return symbols
    except Exception as e:
        logger.error(f"Error fetching RemotePairList: {str(e)}")
        return None


def extract_multiplier_and_symbol(s: str) -> Tuple[int, str]:
    """
    Extracts numeric multiplier and symbol from a string.
    Examples:
        '1000PEPE' -> (1000, 'PEPE')
        '1MBABYDOGE' -> (1000000, 'BABYDOGE')
        'BTC' -> (1, 'BTC')
    """
    # Handle special case for 1M
    if s.startswith("1M"):
        return (1000000, s[2:])

    # Find the first non-numeric character
    for i, char in enumerate(s):
        if not char.isdigit():
            if i > 0:
                multiplier = int(s[:i])
                symbol = s[i:]
                return (multiplier, symbol)
            break

    # No multiplier found
    return (1, s)


def normalize_symbol(s: str) -> Tuple[int, str]:
    """
    Normalizes a symbol by extracting its multiplier and base name.
    """
    multiplier, symbol = extract_multiplier_and_symbol(s)
    return (multiplier, symbol)


def merge_symbol_lists(symbolscout_symbols: Optional[Set[str]], 
                      remotepairlist_symbols: Optional[Set[str]], 
                      merge_strategy: str) -> Optional[Set[str]]:
    if symbolscout_symbols is None and remotepairlist_symbols is None:
        return None
        
    if symbolscout_symbols is None:
        return remotepairlist_symbols
        
    if remotepairlist_symbols is None:
        return symbolscout_symbols

    # Create normalized versions of both sets
    normalized_symbolscout = {normalize_symbol(s) for s in symbolscout_symbols}
    normalized_remotelist = {normalize_symbol(s) for s in remotepairlist_symbols}
    
    # Create dictionaries with symbol as key and multiplier as value
    symbolscout_dict = {symbol: mult for mult, symbol in normalized_symbolscout}
    remotelist_dict = {symbol: mult for mult, symbol in normalized_remotelist}
    
    # Perform the merge operation based on symbol names only
    if merge_strategy == "intersection":
        common_symbols = set(symbolscout_dict.keys()) & set(remotelist_dict.keys())
    else:  # union
        common_symbols = set(symbolscout_dict.keys()) | set(remotelist_dict.keys())
    
    # For each common symbol, use the highest multiplier from either source
    final_symbols = set()
    for symbol in common_symbols:
        multiplier = max(
            symbolscout_dict.get(symbol, 1),
            remotelist_dict.get(symbol, 1)
        )
        if multiplier == 1:
            final_symbols.add(symbol)
        elif multiplier == 1000000:
            final_symbols.add(f"1M{symbol}")
        else:
            final_symbols.add(f"{multiplier}{symbol}")
    
    logger.info(f"Merged symbol lists ({len(final_symbols)} symbols)")
    
    return final_symbols


def normalize_pair_symbol(pair: str) -> str:
    """
    Extract and normalize the base symbol from a trading pair.
    """
    # Handle both formats: "BTC/USDT" and "BTC/USDT:USDT"
    base = pair.split("/")[0]
    return base


def get_combined_symbol_list(config) -> Optional[Set[str]]:
    sync_config = config.get("symbol_list_sync", {})

    if not sync_config.get("enabled", False):
        return None

    symbolscout_symbols = None
    remotepairlist_symbols = None

    if sync_config.get("symbolscout_watchlist", {}).get("enabled", False):
        endpoint = sync_config["symbolscout_watchlist"]["endpoint"]
        symbolscout_symbols = fetch_symbolscout_list(endpoint)

    if sync_config.get("remotepairlist", {}).get("enabled", False):
        endpoint = sync_config["remotepairlist"]["endpoint"]
        remotepairlist_symbols = fetch_remotepairlist(endpoint)

    return merge_symbol_lists(
        symbolscout_symbols,
        remotepairlist_symbols,
        sync_config.get("merge_strategy", "intersection"),
    )
