import math
from typing import List, Dict

def pagination_helper(data: List[dict], page: int, limit: int, total_count: int) -> Dict[str, any]:
    total_pages = math.ceil(total_count / limit) 
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_count": total_count,
        "data": data
    }