FLOOR_A_ZONES = {
    "SKINCARE_BROWSING": {
        "x1": 0,
        "y1": 0,
        "x2": 900,
        "y2": 500
    },
    "PREMIUM_SKINCARE": {
        "x1": 900,
        "y1": 0,
        "x2": 1920,
        "y2": 500
    },
    "PROMO_WALKWAY": {
        "x1": 0,
        "y1": 500,
        "x2": 900,
        "y2": 1080
    },
    "BEAUTY_CONSULTATION": {
        "x1": 900,
        "y1": 500,
        "x2": 1920,
        "y2": 1080
    }      
}


FLOOR_B_ZONES = {
    "BEAUTY_STATION": {
        "x1": 0,
        "y1": 0,
        "x2": 900,
        "y2": 500
    },
    "PREMIUM_MAKEUP": {
        "x1": 900,
        "y1": 0,
        "x2": 1920,
        "y2": 500
    },
    "BROWSING_CORRIDOR": {
        "x1": 0,
        "y1": 500,
        "x2": 900,
        "y2": 1080
    },
    "COLOR_COSMETICS": {
        "x1": 900,
        "y1": 500,
        "x2": 1920,
        "y2": 1080
    }
}

# Queue Zone Configuration
# Defines billing queue zones per floor
FLOOR_A_QUEUE_ZONE = {
    "zone_id": "BILLING_QUEUE_A",
    "x1": 0,
    "y1": 1000,
    "x2": 1920,
    "y2": 1080,
    "description": "Billing queue area for Floor A"
}

FLOOR_B_QUEUE_ZONE = {
    "zone_id": "BILLING_QUEUE_B",
    "x1": 0,
    "y1": 1000,
    "x2": 1920,
    "y2": 1080,
    "description": "Billing queue area for Floor B"
}

# Queue Analytics Configuration
QUEUE_CONFIG = {
    "QUEUE_ABANDON_WINDOW_SECONDS": 600,  # 10 minutes - time window to wait for conversion
    "MIN_QUEUE_WAIT_SECONDS": 3,          # Minimum wait time to count as queue visit
    "MIN_QUEUE_DEPTH_FOR_JOIN": 1,        # Minimum queue depth to emit JOIN event (1 = always)
    "FPS": 30                              # Video frame rate
}