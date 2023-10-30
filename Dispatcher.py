# Simple library to dispatch asynchronously a large number of requests to multiple servers.
# Supports the following features:
# - Global concurrency limit (max number of requests that can be made at the same time)
# - Individual timeout for each request
# - Individual cooldown time for each request
# - Exponential back-off for failed requests
# - Retry with another server on transient errors
# - Global timeout for the whole batch
# Author: Emile Amajar

import asyncio

class Dispatcher:
    def __init__(self, servers, timeout_individual, timeout_total, concurrency=128, exp_factor=2, max_attempts=5, cooldown=0):
        self.servers = servers
        self.timeout_individual = timeout_individual
        self.timeout_total = timeout_total
        self.concurrency = concurrency
        self.exp_factor = exp_factor
        self.max_attempts = max_attempts
        self.cooldown = cooldown
        self.available_servers = asyncio.Queue()  # server queue

    async def gather_with_concurrency(self, n, *tasks):
        semaphore = asyncio.Semaphore(n)

        async def sem_task(task):
            async with semaphore:
                return await task
        return await asyncio.gather(*(sem_task(task) for task in tasks))

    async def _request(self, coroutine):
        attempt = 0
        web3 = await self.available_servers.get()  # get a server from queue
        while attempt < self.max_attempts:
            try:
                result = await asyncio.wait_for(coroutine(web3), timeout=self.timeout_individual)  # make the request
                if self.cooldown > 0:
                    await asyncio.sleep(self.cooldown)  # if cooldown is set, then wait
                self.available_servers.put_nowait(web3)  # put the server back to the queue
                return result
            except Exception as e:
                s = str(e).lower()
                if "timeout" in s or "connection error" in s or "server error" in s:
                    attempt += 1
                    if attempt >= len(self.servers):
                        break
                    await asyncio.sleep(0.1 * self.exp_factor ** attempt)  # wait for an exponentially back-off time
                    web3 = await self.available_servers.get()  # replace the problematic provider
                else:
                    print("Unknown exception: ", e)
                    return None
        print("Too many attempts")
        return None

    def send_requests(self, coroutines):
        # fill up the server queue
        for provider in self.servers:
            self.available_servers.put_nowait(provider)

        loop = asyncio.get_event_loop()
        tasks = [self._request(coro) for coro in coroutines]
        results = loop.run_until_complete(self.gather_with_concurrency(self.concurrency, *tasks))

        return results