def insight_helper(insight)->dict:
   return {
        "id": str(insight.get("_id", None)),
        "sourceType": insight.get("sourceType", None),
        "subject": insight.get("subject", None),
        "category":insight.get("category", None),
        "sender": insight.get("sender", None),
        "contact": insight.get("contact", None),
        "jobDetails":insight.get("jobDetails", None),
        "date": insight.get("date", None),
    }


def insights_helper(insights)->list:
    return [insight_helper(insight) for insight in insights]


def get_operators():
    return {
            'eq': '$eq',
            'ne': '$ne',
            'gt': '$gt',
            'gte': '$gte',
            'lt': '$lt',
            'lte': '$lte',
            'in': '$in',
            'nin': '$nin',
            'regex': '$regex',
            'exists': '$exists',
            'contains': '$regex',
            'starts_with': '$regex',
        }