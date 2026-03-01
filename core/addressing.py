def get_addressed_personalities(address_mode: str) -> list[str]:
    """
    Returns the list of personalities that should respond based on the given mode.
    Valid modes: "ALL", "MELCHIOR", "BALTHASAR", "CASPER".
    Falls back to "ALL" if unrecognized.
    """
    mode = str(address_mode).strip().upper()
    valid_singles = ["MELCHIOR", "BALTHASAR", "CASPER"]
    
    if mode in valid_singles:
        return [mode]
    return valid_singles
