# Notes on current state of the project.

- Initial scope: Research "yield arbitrage" strategies for crypto assets. Exploit data from Syntropy.

- Strategy reference article: https://0xbrainjar.medium.com/pool-pool-yield-arbitrage-powered-by-cross-layer-tricrypto-lp-token-swaps-8d2afeff3e15 Key takeaway is: Optimizing LPing by moving liquidity frequently between exchanges/chains, depending on latest APYs.

- Useful link to check yields on various protocols https://defillama.com/yields

- Note on exposure risks: some protocols only give yields to multiple tokens at the same time e.g. in pairs, etc (Uniswap, SushiSwap, Curve, Balancer). Single-asset protocols can provide less risks in that regard (Aave, Bancor, Compound) but also often only in stablecoins. (Thus providing less yield ??)

- Only some tokens are available on multiple chains, Although the ones with top-market cap are usually available on most chains.

- Need to only consider tokens that are easily bridged between chains to make matters simpler. Can later choose to add more complex bridging mechanisms.

- Strategy would probably benefit from dynamically adjusting exposure from one token to another, depending on current yields.
That is to say, if we start with $10k in USDC@10% and $10k in ETH@15%, we should consider moving some of the USDC to ETH. Not necessarily all of it, to stay diversified.

- Live mempool data could be exploited to anticipate large drawdowns from single transactions, rugpulls, etc... The mechanism would only work some of the time (like 50%), as some transactions are never announced in the mempool, but it could be a good way to avoid some losses.

- Thoughts on rebalancing frequency: ideally, we would want to rebalance as frequently as possible, to rake in as much LP profit as possible, everytime some pool on some platform seems to have increased trading activity. The only limiting factors are the time opportunity when transferring funds cross-chain (which take some time, during which we are not LPing the capital), and more importantly the transaction fees. If we consider a total capital of $100k, generating 40% APY yield, the absolute profits are ~$110 per day. If rebalancing costs $10 per action and is done once a day, it cuts profits by 10%. There can be multiple rebalancing strategies:
    - Fixed time interval: rebalance every X hours, days, weeks, months, etc... Simpler method, but doesn't take into account the current state of the market.
    - Linear opportunity cost: dynamically adjust the rebalancing period depending on the difference between the APYs. The greater the difference, the sooner we should consider rebalancing. Find suitable proportionality constant.

- Strategy downside: doesn't use Syntropy data to its full potential. Could be done without Syntropy data, by just checking yields on various protocols, time frames are much larger than block periods.

- Strategy's next frontier: use live mempool defi transaction data to perform JIT liquidity sandwiching. When a large DeFi transaction is detected, send a private transaction bundle that frontruns the target tx by providing large amounts of liquidity. The target tx is then followed in the bundle, and finally the second 'leg' of the sandwich is the liquidity pulling transaction. The JIT bot will have gathered the trading fees + the MEV from the manipulated slippage. This demands large capital to work. Live example of a JIT MEV bot https://etherscan.io/address/0xa69babef1ca67a37ffaf7a485dfff3382056e78c 

Current syntropy public chain data:
    - Cosmos
    - Aptos
    - Ethereum
    - Arbitrum
    - Base
    - Solana

Tokens that are currently traded on most of these chains:

- WETH, USDC, USDT, DAI, BNB, WBTC, BUSD, 


- [ ] Find acceptable exchanges for generating yield on each chain.
    Criteria:
        - [ ] Maturity of the exchange. Too new, too risky.
        - [ ] Easy composability with other protocols.
        - [ ] No locking period for staking/LPing. Ignore APYs that require locking periods. Only liquid positions.

    Results per chain:
        - [ ] Cosmos: Osmosis
        - [ ] Aptos:
        - [ ] Ethereum: Uniswap, SushiSwap, Curve, Balancer, Bancor
        - [ ] Arbitrum: Curve
        - [ ] Base: Curve, Harvest
        - [ ] Solana: Raydium

    Results per protocol:
        - [ ] Uniswap V2 (pair exposure)
        - [ ] Uniswap V3 (pair exposure)
        - [ ] SushiSwap (pair exposure)
        - [ ] Curve (stablecoin exposure)


- [ ] Check services provided by yield aggregators.
    - [ ] Harvest
    - [ ] Yearn
    - [ ] Convex
    - [ ] Beefy
    - [ ] Zapper
    - [ ] Zerion


- [ ] Manually check current advertised APY on each platform, for major tokens:
    - [ ] USDC:
    - [ ] USDT:
    - [ ] ETH:

# Current technical progress

## Initial research phase
### Reproducing findings from medium article
- [x] Script to display past APY data for a specific Curve pool
- [x] Script to display past APY data for multiple Curve pools, on the same chain
- [ ] APY data for Curve pools on multiple chains
- [ ] Compute theoretical max strategy APY under various assumptions
    - [ ] Stay in stables, with hindsight
    - [ ] Stay in stables+ETH, with hindsight

### Experiment with realistic strategy
    - [ ] Stables without hindsight
        - [ ] Fixed interval rebalancing, fixed fees
        - [ ] Fixed interval rebalancing, network fees
        - [ ] Linear opportunity cost rebalancing, network fees

### Integrate additional protocols
    - [ ] Uniswap V2
    - [ ] SushiSwap
    - [ ] Uniswap V3
    - [ ] Balancer
    - [ ] Bancor
