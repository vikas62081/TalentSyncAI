from enum import Enum


def chart_helper(chart)->dict:
   return {
        "label": chart.get("_id", None),
        "count": chart.get("count", None),
    }


def charts_helper(charts)->list:
    return [chart_helper(chart) for chart in charts]

class InsighFilter(str, Enum):
    DATE = "date"
    VENDOR = "vendor"
    CLIENT = "client"
    EMAIL = "email"
    CITY = "city"
    STATE="state"
    PRIMARY_SKILL="primary_skill"
    TECHNOLOGY = "technology"
    CATEGORY = "category"
    LOCATION="location"