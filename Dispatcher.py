# Simple library to dispatch asynchronously a large number of requests to multiple servers.
# Supports the following features:
# - Global concurrency limit (max number of requests that can be made at the same time)
# - Individual timeout for each request
# - Exponential back-off for failed requests
# - Retry with another server on transient errors
# - Global timeout for the whole batch
# Author: Emile Amajar

import asyncio

class Dispatcher:
    def __init__(self, servers, timeout_individual, timeout_total, concurrency=128, exp_factor=2, max_attempts=5):
        self.servers = servers
        self.timeout_individual = timeout_individual
        self.timeout_total = timeout_total
        self.concurrency = concurrency
        self.exp_factor = exp_factor
        self.max_attempts = max_attempts
        self.available_servers = asyncio.Queue()

    def send_requests(self, coroutines):
        # Fill up the queue with servers
        for provider in self.servers:
            self.available_servers.put_nowait(provider)
        # Create a semaphore and an event loop, and impose a total timeout
        self.semaphore = asyncio.Semaphore(self.concurrency)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(
            asyncio.wait(
                [self._request(coro) for coro in coroutines],
                timeout=self.timeout_total,
                return_when=asyncio.ALL_COMPLETED
            )
        )
        done_futures, _ = loop.run_until_complete(future)
        # Get result from futures
        results = [fut.result() for fut in done_futures if not fut.cancelled() and fut.exception() is None]
        return results

    async def _request(self, coroutine):
        attempt = 0
        web3 = await self.available_servers.get()
        while attempt < self.max_attempts:
            try:
                # Wait for a free slot from the semaphore before making the request
                async with self.semaphore:
                    result = await asyncio.wait_for(coroutine(web3), timeout=self.timeout_individual)
                    self.available_servers.put_nowait(web3)
                    return result
            except Exception as e:
                # If the exception contains: timeout, connection error, or server error, then retry
                s = str(e).lower()
                if "timeout" in s or "connection error" in s or "server error" in s:
                    # Increase the attempt count and wait for an exponentially back-off time
                    attempt += 1
                    if attempt >= len(self.servers):
                        break
                    await asyncio.sleep(0.1 * self.exp_factor ** attempt)
                    # Replace the problematic provider with another one from the list
                    web3 = await self.available_servers.get()
                else:
                    # If the exception is not one of the above, then return None
                    print("Unknown exception: ", e)
                    return None
                
        # Too many attempts, return None
        print("Too many attempts")
        return None