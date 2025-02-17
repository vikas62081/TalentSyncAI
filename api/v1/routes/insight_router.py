from datetime import datetime
from typing import Optional
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from api.v1.services.insight_service import InsightService
from api.v1.services.scheduler_service import SchedulerService
from schemas.chart import InsighFilter

insight_router=APIRouter(tags=["Insights"])
insight_service=InsightService()
# schedule_service=SchedulerService()
    
@insight_router.get("")
def get_insights(filters:Optional[str] = None,from_date:Optional[datetime]=None,to_date:Optional[datetime]=None,page: int = 1, limit: int = 10):
    return insight_service.get_insights(filters,from_date,to_date,page,limit)

@insight_router.get("/charts")
def get_chart_data(category:InsighFilter,from_date:datetime=None,to_date:datetime=None,limit:int=15):
    return insight_service.get_chart_data(category,from_date,to_date,limit)

@insight_router.get("/charts/daily")
def get_chart_data_day_wise(category:InsighFilter,from_date:datetime=None,to_date:datetime=None):
    return insight_service.get_chart_data_day_wise(category,from_date,to_date)

@insight_router.get("/{id}")
def get_insight_raw_content_by_id(id:str):
    insight= insight_service.get_insight_by_id(id)
    return insight

@insight_router.get("/{id}/raw",response_class=HTMLResponse)
def get_insight_raw_content_by_id(id:str):
    raw= insight_service.get_insight_raw_content(id)
    return raw

# @insight_router.get("/jobs/run")
# def get_jobs_from_email():
#     schedule_service.add_task()