import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class AsyncAPIService:
    def __init__(self, max_concurrent: int = 5):
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a single API request with rate limiting"""
        async with self.semaphore:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            try:
                method = request_data.get('method', 'POST')
                url = request_data['url']
                headers = request_data.get('headers', {})
                data = request_data.get('data')
                
                async with self.session.request(method, url, headers=headers, json=data) as response:
                    result = await response.json()
                    return {
                        'success': True,
                        'data': result,
                        'status_code': response.status,
                        'request_id': request_data.get('id', 'unknown')
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'request_id': request_data.get('id', 'unknown')
                }
    
    async def batch_api_calls(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple API calls concurrently"""
        if not requests:
            return []
        
        tasks = [self._make_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'request_id': requests[i].get('id', f'request_{i}')
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def retry_failed_requests(self, failed_requests: List[Dict[str, Any]], max_retries: int = 3) -> List[Dict[str, Any]]:
        """Retry failed requests with exponential backoff"""
        results = []
        
        for request in failed_requests:
            for attempt in range(max_retries):
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                result = await self._make_request(request)
                
                if result['success']:
                    results.append(result)
                    break
                elif attempt == max_retries - 1:
                    results.append(result)  # Final failure
        
        return results
