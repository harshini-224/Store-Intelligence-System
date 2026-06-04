"""In-memory event storage for the API.

Production deployments would replace this with a database.
"""

EVENTS = []
SEEN_EVENT_IDS = set()