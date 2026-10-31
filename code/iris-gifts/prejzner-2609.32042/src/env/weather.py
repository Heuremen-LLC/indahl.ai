"""weather.py (ours): the tool environment the tasks call.

Five tools over a fixed table of 52 cities and a small neighbour graph. Standard library only.

Transcribed constants (data, not logic): the CITIES table and the NEIGHBOURS graph below are copied from the benchmark's
src/polagentbench/environments/weather.py, because a city table cannot be reconstructed from the released step records
(only the cities some model asked about appear there). constants_check.py compares both tables against that file read as
text, and acceptance.py checks every tool result in the released records against what this module returns.

Observation shape: {"ok": True, "result": {...}} or {"ok": False, "error": "...", "error_code": "..."}.
State shape: {"alerts_sent": [...], "lookup_log": [...]}; lookup_log has one entry per city lookup.
"""
import unicodedata

# Source: environments/weather.py of the benchmark, _CITIES. Order is the order of the source.
CITIES = {
    "Warszawa": {"temperature_c": 9.0, "condition": "cloudy", "humidity_pct": 70},
    "Kraków": {"temperature_c": 7.5, "condition": "cloudy", "humidity_pct": 72},
    "Łódź": {"temperature_c": 8.0, "condition": "rain", "humidity_pct": 80},
    "Wrocław": {"temperature_c": 10.0, "condition": "clear", "humidity_pct": 60},
    "Poznań": {"temperature_c": 8.5, "condition": "rain", "humidity_pct": 78},
    "Gdańsk": {"temperature_c": 7.0, "condition": "windy", "humidity_pct": 82},
    "Szczecin": {"temperature_c": 9.0, "condition": "cloudy", "humidity_pct": 75},
    "Bydgoszcz": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 73},
    "Lublin": {"temperature_c": 7.0, "condition": "clear", "humidity_pct": 65},
    "Białystok": {"temperature_c": 5.5, "condition": "rain", "humidity_pct": 81},
    "Katowice": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 70},
    "Gdynia": {"temperature_c": 7.5, "condition": "windy", "humidity_pct": 80},
    "Częstochowa": {"temperature_c": 7.5, "condition": "cloudy", "humidity_pct": 71},
    "Radom": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 70},
    "Sosnowiec": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 70},
    "Toruń": {"temperature_c": 8.5, "condition": "rain", "humidity_pct": 76},
    "Kielce": {"temperature_c": 7.0, "condition": "cloudy", "humidity_pct": 69},
    "Rzeszów": {"temperature_c": 7.0, "condition": "clear", "humidity_pct": 64},
    "Gliwice": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 70},
    "Olsztyn": {"temperature_c": 6.5, "condition": "rain", "humidity_pct": 79},
    "Bielsko-Biała": {"temperature_c": 6.0, "condition": "snow", "humidity_pct": 85},
    "Opole": {"temperature_c": 9.0, "condition": "clear", "humidity_pct": 62},
    "Tarnów": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 68},
    "Płock": {"temperature_c": 8.5, "condition": "cloudy", "humidity_pct": 72},
    "Elbląg": {"temperature_c": 7.0, "condition": "windy", "humidity_pct": 80},
    "Włocławek": {"temperature_c": 8.5, "condition": "rain", "humidity_pct": 77},
    "Zakopane": {"temperature_c": 2.0, "condition": "snow", "humidity_pct": 88},
    "Świnoujście": {"temperature_c": 8.0, "condition": "windy", "humidity_pct": 84},
    "Sopot": {"temperature_c": 7.5, "condition": "windy", "humidity_pct": 81},
    "Zielona Góra": {"temperature_c": 9.5, "condition": "clear", "humidity_pct": 63},
    "Żory": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 70},
    "Tatry": {"temperature_c": -5.0, "condition": "snow", "humidity_pct": 88},
    "London": {"temperature_c": 11.0, "condition": "rain", "humidity_pct": 78},
    "Paris": {"temperature_c": 12.0, "condition": "cloudy", "humidity_pct": 70},
    "Berlin": {"temperature_c": 10.0, "condition": "cloudy", "humidity_pct": 72},
    "Madrid": {"temperature_c": 17.0, "condition": "clear", "humidity_pct": 45},
    "Rome": {"temperature_c": 18.0, "condition": "clear", "humidity_pct": 55},
    "Vienna": {"temperature_c": 11.0, "condition": "cloudy", "humidity_pct": 65},
    "Prague": {"temperature_c": 10.0, "condition": "cloudy", "humidity_pct": 67},
    "Budapest": {"temperature_c": 12.0, "condition": "clear", "humidity_pct": 60},
    "Amsterdam": {"temperature_c": 11.0, "condition": "rain", "humidity_pct": 80},
    "Brussels": {"temperature_c": 11.0, "condition": "cloudy", "humidity_pct": 75},
    "Stockholm": {"temperature_c": 5.0, "condition": "cloudy", "humidity_pct": 73},
    "Oslo": {"temperature_c": 4.0, "condition": "snow", "humidity_pct": 80},
    "Copenhagen": {"temperature_c": 8.0, "condition": "cloudy", "humidity_pct": 78},
    "Helsinki": {"temperature_c": 3.0, "condition": "snow", "humidity_pct": 82},
    "Lisbon": {"temperature_c": 16.0, "condition": "clear", "humidity_pct": 60},
    "Athens": {"temperature_c": 19.0, "condition": "clear", "humidity_pct": 50},
    "Dublin": {"temperature_c": 10.0, "condition": "rain", "humidity_pct": 82},
    "Reykjavik": {"temperature_c": 4.0, "condition": "windy", "humidity_pct": 80},
    "New York": {"temperature_c": 14.0, "condition": "cloudy", "humidity_pct": 65},
    "Tokyo": {"temperature_c": 17.0, "condition": "clear", "humidity_pct": 60},
}

# Source: environments/weather.py of the benchmark, _NEIGHBOURS. Graph order is the order of the lists.
NEIGHBOURS = {
    "Warszawa": [("Łódź", 130), ("Płock", 110), ("Radom", 100), ("Lublin", 165)],
    "Kraków": [("Katowice", 80), ("Tarnów", 85), ("Zakopane", 105), ("Opole", 175)],
    "Wrocław": [("Opole", 100), ("Poznań", 165), ("Katowice", 195)],
    "Gdańsk": [("Sopot", 15), ("Gdynia", 25), ("Elbląg", 60), ("Olsztyn", 170)],
    "Łódź": [("Warszawa", 130), ("Częstochowa", 120), ("Płock", 100)],
    "Poznań": [("Wrocław", 165), ("Bydgoszcz", 130), ("Zielona Góra", 145)],
    "Katowice": [("Kraków", 80), ("Gliwice", 25), ("Sosnowiec", 15), ("Bielsko-Biała", 50)],
    "Gdynia": [("Sopot", 5), ("Gdańsk", 25)],
    "Sopot": [("Gdynia", 5), ("Gdańsk", 15)],
}

TOOL_NAMES = ["get_weather", "get_forecast", "send_weather_alert", "convert_temperature", "find_nearest_city"]
SEVERITIES = ("low", "medium", "high")
UNITS = ("celsius", "fahrenheit")


def fold(name):
    """Diacritic-insensitive lookup key: NFKD, drop combining marks, l-stroke to l, lower case, trim."""
    decomposed = unicodedata.normalize("NFKD", name)
    kept = "".join(c for c in decomposed if not unicodedata.combining(c))
    kept = kept.replace("ł", "l").replace("Ł", "L")
    return kept.lower().strip()


_BY_FOLD = {fold(c): c for c in CITIES}


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _not_found(raw):
    return {"ok": False, "error": "City %r not found in database." % (raw,), "error_code": "CITY_NOT_FOUND"}


def _bad(error, code):
    return {"ok": False, "error": error, "error_code": code}


class WeatherEnv:
    def __init__(self):
        self.alerts = []
        self.log = []
        self.strict = False
        self.overrides = {}

    # state ---------------------------------------------------------------
    def reset(self, initial_state):
        """initial_state may carry alerts_sent, __strict_match (exact names only) and __overrides ({"cities": {...}})."""
        self.alerts = list(initial_state.get("alerts_sent", []))
        self.log = []
        self.strict = bool(initial_state.get("__strict_match", False))
        self.overrides = {}
        ov = initial_state.get("__overrides") or {}
        cities = ov.get("cities") if isinstance(ov, dict) else None
        if isinstance(cities, dict):
            self.overrides = {k: dict(v) for k, v in cities.items() if isinstance(v, dict)}

    def snapshot(self):
        return {"alerts_sent": list(self.alerts), "lookup_log": list(self.log)}

    # lookup --------------------------------------------------------------
    def _record(self, canonical):
        rec = dict(CITIES[canonical])
        rec.update(self.overrides.get(canonical) or {})
        return rec

    def _find(self, raw):
        """Return (canonical, record) or (None, None); every call appends one lookup_log entry."""
        entry = {"input": raw, "canonical": None, "diacritic_corrupted": False, "found": False}
        if not isinstance(raw, str) or not raw.strip():
            self.log.append(entry)
            return None, None
        if self.strict:
            canonical = raw if raw in CITIES else None
        else:
            canonical = _BY_FOLD.get(fold(raw))
        if canonical is None:
            self.log.append(entry)
            return None, None
        entry["canonical"] = canonical
        entry["found"] = True
        if not self.strict:
            entry["diacritic_corrupted"] = raw != canonical
        self.log.append(entry)
        return canonical, self._record(canonical)

    # dispatch ------------------------------------------------------------
    def call(self, name, args):
        fn = getattr(self, "_t_" + name, None) if name in TOOL_NAMES else None
        if fn is None:
            return _bad("Unknown tool: %r. Available: %s." % (name, TOOL_NAMES), "UNKNOWN_TOOL")
        return fn(args)

    def _t_get_weather(self, args):
        city, rec = self._find(args.get("city"))
        if city is None:
            return _not_found(args.get("city", ""))
        out = {"city": city}
        out.update(rec)
        return {"ok": True, "result": out}

    def _t_get_forecast(self, args):
        city, rec = self._find(args.get("city"))
        if city is None:
            return _not_found(args.get("city", ""))
        days = args.get("days")
        if not _is_int(days) or days < 1 or days > 7:
            return _bad("days must be an integer between 1 and 7.", "INVALID_RANGE")
        base = rec["temperature_c"]
        rows = []
        for i in range(days):
            rows.append({"day": i + 1, "temperature_c": round(base + (i - days / 2) * 0.5, 1),
                         "condition": rec["condition"]})
        return {"ok": True, "result": {"city": city, "days": days, "forecast": rows}}

    def _t_send_weather_alert(self, args):
        city, _ = self._find(args.get("city"))
        if city is None:
            return _not_found(args.get("city", ""))
        severity = args.get("severity")
        if severity not in SEVERITIES:
            return _bad("severity must be one of: %s." % (sorted(SEVERITIES),), "INVALID_ENUM")
        message = args.get("message")
        if not isinstance(message, str) or not message.strip():
            return _bad("message must be a non-empty string.", "INVALID_ARGUMENT")
        alert = {"city": city, "severity": severity, "message": message}
        self.alerts.append(alert)
        return {"ok": True, "result": {"alert": alert, "alert_id": len(self.alerts)}}

    def _t_convert_temperature(self, args):
        value, src, dst = args.get("value"), args.get("from_unit"), args.get("to_unit")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return _bad("value must be a number.", "INVALID_ARGUMENT")
        if src not in UNITS or dst not in UNITS:
            return _bad("unit must be one of: %s." % (sorted(UNITS),), "INVALID_ENUM")
        v = float(value)
        if src == dst:
            out = v
        elif src == "celsius":
            out = v * 9 / 5 + 32
        else:
            out = (v - 32) * 5 / 9
        return {"ok": True, "result": {"value": round(out, 2), "from_unit": src, "to_unit": dst}}

    def _t_find_nearest_city(self, args):
        city, _ = self._find(args.get("reference_city"))
        if city is None:
            return _not_found(args.get("reference_city", ""))
        limit = args.get("max_distance_km")
        if not _is_int(limit) or limit <= 0:
            return _bad("max_distance_km must be a positive integer.", "INVALID_ARGUMENT")
        near = [name for name, km in NEIGHBOURS.get(city, []) if km <= limit]
        return {"ok": True, "result": {"reference_city": city, "max_distance_km": limit, "cities": near}}
