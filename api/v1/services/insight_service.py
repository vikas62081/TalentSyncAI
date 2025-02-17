from datetime import datetime, timedelta 
import logging
import re
from typing import Any, Dict, Tuple
from bson import ObjectId
from pymongo.errors import PyMongoError

from config.mongo_db import MongoDBManager
from config.collections import JOB_INSINGHT
from exceptions.not_found_exception import NotFoundException
from schemas.pagination import pagination_helper
from schemas.chart import InsighFilter
from schemas.insight import get_operators, insight_helper, insights_helper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightService:
    """
    Service class to store, retrieve, and delete insights from MongoDB.
    """
    def __init__(self):
        """
        Initialize the InsightService with a MongoDB connection.
        """
        manager=MongoDBManager()
        self.collection =manager.get_collection(JOB_INSINGHT)
        
    def get_insights(self, filters, from_date, to_date, page, limit):
        if page < 1 or limit < 1:
            raise NotFoundException("Page and limit must be positive integers.")
        
        from_date, to_date = self.get_date_range(from_date, to_date)
        mongo_query = self.build_mongo_query(filters, from_date, to_date)
        
        skip = (page - 1) * limit
        insights = self.collection.find(mongo_query).sort("date", -1).skip(skip).limit(limit)
        return pagination_helper(insights_helper(insights), page, limit, self.get_total_count(mongo_query))
    
    def get_total_count(self,query={}) -> int:
        return self.collection.count_documents(query)
    
    def get_insight_by_id(self,id):
        insight = self.collection.find_one({"_id":ObjectId(id)})
        if not insight:
            raise NotFoundException(f"Insight not found with id {id}")
        return insight_helper(insight)
    
    def get_insight_raw_content(self,id):
        insight = self.collection.find_one({"_id":ObjectId(id)})
        if not insight:
            raise NotFoundException(f"Insight not found with id {id}")
        return insight["rawContent"]
    
    def get_chart_data(self,category:InsighFilter,from_date=None,to_date=None,limit=15):
        # Get the key field and date range
        _key = self.get_insight_key(category)
        from_date, to_date = self.get_date_range(from_date, to_date)
    
        logger.info(f"Key: {_key}, From date: {from_date}, To date: {to_date}")
        # Build the aggregation pipeline
        pipeline = [
            {
                "$addFields": {
                    "date": {
                        "$dateFromParts": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        }
                    }
                }    
            },
            {"$match": {"date": {"$gte": from_date, "$lte": to_date}}},
            {"$unwind": f"${_key}"},
            {"$group": {"_id": f"${_key}", "value": {"$sum": 1}}},
            {"$project": {"label": "$_id", "value": 1, "_id": 0}},
            {"$sort": {"value": -1}},
            {"$limit": limit}
        ]
        return list(self.collection.aggregate(pipeline))
    
    def get_chart_data_day_wise(self, category: InsighFilter, from_date=None, to_date=None):
        # Get the key field and date range
        _key = self.get_insight_key(category)

        from_date, to_date = self.get_date_range(from_date, to_date)

        logger.info(f"Key: {_key}, From date: {from_date}, To date: {to_date}")

        # Build the aggregation pipeline
        pipeline = [
            {
                "$addFields": {
                    "day": {
                         "$dateFromParts": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        }
                    }
                }
            },
            {"$match": {"date": {"$gte": from_date, "$lte": to_date}}},
            {"$unwind": f"${_key}"},
            {
                "$group": {
                    "_id": {"day": "$day", "label": f"${_key}"},
                    "value": {"$sum": 1}
                }
            },
            {"$sort": {"value": -1}},
            {"$group": {
                    "_id": "$_id.day",
                    "top_entry": {"$first": {"label": "$_id.label", "value": "$value"}}
                }},
            {
                "$project": {
                    "date": "$_id",
                    "label": "$top_entry.label",
                    "value": "$top_entry.value",
                    "_id": 0
                }
            },
            {"$sort": {"date": 1}}
        ]

        return list(self.collection.aggregate(pipeline))
    
    def get_insight_key(self,category: InsighFilter) -> str:
        """
        Map the given InsighFilter to the corresponding field in the collection.
        Raises ValueError if the key is invalid.
        """
        key_mapping = {
            InsighFilter.CLIENT: "jobDetails.company",
            InsighFilter.VENDOR: "contact.company",
            InsighFilter.CITY: "jobDetails.city",
            InsighFilter.STATE: "jobDetails.state",
            InsighFilter.LOCATION: "jobDetails.location",
            InsighFilter.EMAIL: "sender.from",
            InsighFilter.TECHNOLOGY: "jobDetails.skills",
            InsighFilter.PRIMARY_SKILL: "jobDetails.primarySkill",
            InsighFilter.DATE: "date",
            InsighFilter.CATEGORY:"category"
        }
        
        _key = key_mapping.get(category)
        if not _key:
            raise ValueError(f"Invalid InsighFilter provided: {category}")
        return _key
    
    def get_date_range(self,from_date=None, to_date=None,default_days_range=30) -> Tuple[datetime, datetime]:
        """
        Calculate the date range. If no dates are provided, defaults to the past 30 days.
        Returns a tuple of (from_date, to_date).
        """
        today = datetime.now()
        from_date = from_date or (today - timedelta(days=default_days_range))
        to_date = to_date or today
        return from_date, to_date

    def add_insight(self, insight):
        """
        Add a new insight or update an existing one in MongoDB.

        :param insight: Unique identifier for the insight (e.g., a UUID or string).
        """
        try:
            # Insert or update insight
            result = self.collection.insert_one(insight)
            print(f"Insight Added for ID: {result.inserted_id}")
        except PyMongoError as e:
            print(f"Failed to add insight: {e}")
            
    def is_insight_already_exsit(self,sender_email,email_subject):
        query = {"subject": email_subject, "contact.email": sender_email}
        result = self.collection.find_one(query)
        return result is not None
    
    def parse_value(self, value_str, field=None):
        try:
            return int(value_str)
        except ValueError:
            pass
        try:
            return float(value_str)
        except ValueError:
            pass
        return value_str
    
    def build_mongo_query(self, filters: str, from_date: datetime, to_date: datetime):
        mongo_query = {"date": {"$gte": from_date, "$lte": to_date}}
        if filters:
            if isinstance(filters, str):
                filters = filters.split(',')
            for filter_str in filters:
                self.apply_filter_to_query(filter_str, mongo_query)
        return mongo_query
    
    def apply_filter_to_query(self, filter_str: str, mongo_query: Dict[str, Any]):
        parts = filter_str.split(':', 2)
        if len(parts) != 3:
            return
        
        field, op, val_str = parts
        field=self.get_insight_key(field)
        
        if op in ['contains', 'starts_with']:
            self.apply_regex_filter(field, op, val_str, mongo_query)
        else:
            self.apply_standard_filter(field, op, val_str, mongo_query, get_operators())
    
    def apply_regex_filter(self, field: str, op: str, val_str: str, mongo_query: Dict[str, Any]):
        escaped_val = re.escape(val_str)
        if op == 'contains':
            regex_pattern = f'.*{escaped_val}.*'
        else:  # starts_with
            regex_pattern = f'^{escaped_val}'
        condition = {"$regex": regex_pattern, "$options": "i"}
        mongo_query[field] = condition
        
    def apply_standard_filter(self, field: str, op: str, val_str: str, mongo_query: Dict[str, Any], operator_map: Dict[str, str]):
        mongo_op = operator_map.get(op)
        if not mongo_op:
            return  # Skip unknown operators
        
        if mongo_op == '$exists':
            val = val_str.lower() == 'true'
            mongo_query[field] = {mongo_op: val}
        elif mongo_op in ('$in', '$nin'):
            val_list = val_str.split(',')
            parsed_list = [self.parse_value(v, field) for v in val_list]
            mongo_query[field] = {mongo_op: parsed_list}
        elif mongo_op == '$regex':
            mongo_query[field] = {mongo_op: val_str}
        else:
            val = self.parse_value(val_str, field)
            if field in mongo_query:
                existing = mongo_query[field]
                if isinstance(existing, dict):
                    existing[mongo_op] = val
                else:
                    mongo_query[field] = {'$eq': existing, mongo_op: val}
            else:
                mongo_query[field] = {mongo_op: val}



