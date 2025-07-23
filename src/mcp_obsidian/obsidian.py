import httpx
import urllib.parse
import os
from typing import Any

class Obsidian():
    def __init__(
            self, 
            api_key: str,
            protocol: str = os.getenv('OBSIDIAN_PROTOCOL', 'https').lower(),
            host: str = str(os.getenv('OBSIDIAN_HOST', '127.0.0.1')),
            port: int = int(os.getenv('OBSIDIAN_PORT', '27124')),
            verify_ssl: bool = False,
        ):
        self.api_key = api_key
        
        if protocol == 'http':
            self.protocol = 'http'
        else:
            self.protocol = 'https' # Default to https for any other value, including 'https'

        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.timeout = (3.0, 6.0) # httpx uses float for timeout

    def get_base_url(self) -> str:
        return f'{self.protocol}://{self.host}:{self.port}'
    
    def _get_headers(self) -> dict:
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        return headers

    async def _safe_call(self, async_fn):
        try:
            return await async_fn()
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            code = error_data.get('errorCode', -1) 
            message = error_data.get('message', '<unknown>')
            raise Exception(f"Error {code}: {message}")
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {str(e)}")

    async def list_files_in_vault(self) -> Any:
        url = f"{self.get_base_url()}/vault/"
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                response.raise_for_status()
                return response.json()['files']

        return await self._safe_call(call_fn)

    async def list_files_in_dir(self, dirpath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{dirpath}/"
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                response.raise_for_status()
                return response.json()['files']

        return await self._safe_call(call_fn)

    async def get_file_contents(self, filepath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"
    
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                response.raise_for_status()
                return response.text

        return await self._safe_call(call_fn)
    
    async def get_batch_file_contents(self, filepaths: list[str]) -> str:
        result = []
        
        for filepath in filepaths:
            try:
                content = await self.get_file_contents(filepath)
                result.append(f"# {filepath}\n\n{content}\n\n---\n\n")
            except Exception as e:
                result.append(f"# {filepath}\n\nError reading file: {str(e)}\n\n---\n\n")
                
        return "".join(result)

    async def search(self, query: str, context_length: int = 100) -> Any:
        url = f"{self.get_base_url()}/search/simple/"
        params = {
            'query': query,
            'contextLength': context_length
        }
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.post(url, headers=self._get_headers(), params=params)
                response.raise_for_status()
                return response.json()

        return await self._safe_call(call_fn)
    
    async def append_content(self, filepath: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.post(
                    url, 
                    headers=self._get_headers() | {'Content-Type': 'text/markdown'}, 
                    content=content
                )
                response.raise_for_status()
                return None

        return await self._safe_call(call_fn)
    
    async def patch_content(self, filepath: str, operation: str, target_type: str, target: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        headers = self._get_headers() | {
            'Content-Type': 'text/markdown',
            'Operation': operation,
            'Target-Type': target_type,
            'Target': urllib.parse.quote(target)
        }
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.patch(url, headers=headers, content=content)
                response.raise_for_status()
                return None

        return await self._safe_call(call_fn)

    async def put_content(self, filepath: str, content: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.put(
                    url, 
                    headers=self._get_headers() | {'Content-Type': 'text/markdown'}, 
                    content=content
                )
                response.raise_for_status()
                return None

        return await self._safe_call(call_fn)
    
    async def delete_file(self, filepath: str) -> Any:
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.delete(url, headers=self._get_headers())
                response.raise_for_status()
                return None
            
        return await self._safe_call(call_fn)
    
    async def search_json(self, query: dict) -> Any:
        url = f"{self.get_base_url()}/search/"
        
        headers = self._get_headers() | {
            'Content-Type': 'application/vnd.olrapi.jsonlogic+json'
        }
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=query)
                response.raise_for_status()
                return response.json()

        return await self._safe_call(call_fn)
    
    async def get_periodic_note(self, period: str, type: str = "content") -> Any:
        url = f"{self.get_base_url()}/periodic/{period}/"
        
        async def call_fn():
            headers = self._get_headers()
            if type == "metadata":
                headers['Accept'] = 'application/vnd.olrapi.note+json'
            
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text

        return await self._safe_call(call_fn)
    
    async def get_recent_periodic_notes(self, period: str, limit: int = 5, include_content: bool = False) -> Any:
        url = f"{self.get_base_url()}/periodic/{period}/recent"
        params = {
            "limit": limit,
            "includeContent": include_content
        }
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers(), params=params)
                response.raise_for_status()
                return response.json()

        return await self._safe_call(call_fn)
    
    async def get_recent_changes(self, limit: int = 10, days: int = 90) -> Any:
        query_lines = [
            "TABLE file.mtime",
            f"WHERE file.mtime >= date(today) - dur({days} days)",
            "SORT file.mtime DESC",
            f"LIMIT {limit}"
        ]
        dql_query = "\n".join(query_lines)
        
        url = f"{self.get_base_url()}/search/"
        headers = self._get_headers() | {
            'Content-Type': 'application/vnd.olrapi.dataview.dql+txt'
        }
        
        async def call_fn():
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    content=dql_query.encode('utf-8')
                )
                response.raise_for_status()
                return response.json()

        return await self._safe_call(call_fn)