def ask_ai(user_query: str) -> str:
    """
    Interpret user query and return filter instructions.
    """
    query = user_query.lower()
    today = datetime.now().date()

    if "yesterday" in query:
        return "yesterday"
    elif "today" in query:
        return "today"
    elif "last month" in query:
        return "last_month"
    else:
        return "all"
