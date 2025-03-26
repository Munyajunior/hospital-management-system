# core/batching.py
from functools import wraps
from typing import Callable, Coroutine, Any, TypeVar
from fastapi import HTTPException
import asyncio

T = TypeVar('T')

def batch_query(batch_size: int = 100):
    """
    Decorator for processing database queries in batches.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if 'ids' in kwargs:
                ids = kwargs['ids']
                results = []
                
                # Process in batches
                for i in range(0, len(ids), batch_size):
                    batch_ids = ids[i:i + batch_size]
                    kwargs['ids'] = batch_ids
                    try:
                        batch_results = await func(*args, **kwargs)
                        results.extend(batch_results)
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Batch processing failed: {str(e)}"
                        )
                return results
            return await func(*args, **kwargs)
        return wrapper
    return decorator