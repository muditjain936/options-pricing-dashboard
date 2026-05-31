import numpy as np

def binomial_tree(S, K, T, r, sigma, option_type='call', n_steps=100):
    """
    Prices an option using the Cox-Ross-Rubinstein (CRR) Binomial Tree.

    How it works:
    - Divides time T into n_steps small intervals
    - At each step, stock can go UP by factor u or DOWN by factor d
    - Builds a tree of all possible stock prices at expiry
    - Works backwards from expiry to get today's option price

    Parameters:
        S           : Current stock price
        K           : Strike price
        T           : Time to expiry (in years)
        r           : Risk-free rate
        sigma       : Volatility
        option_type : 'call' or 'put'
        n_steps     : Number of tree steps (more = more accurate)
    """

    # Step 1: Calculate time interval per step
    dt = T / n_steps

    # Step 2: Up and down factors (CRR parametrization)
    u = np.exp(sigma * np.sqrt(dt))   # up move factor
    d = 1 / u                          # down move factor (symmetric)

    # Step 3: Risk-neutral probability of an up move
    # This is NOT the real-world probability — it's the probability
    # that makes the expected return equal to the risk-free rate
    p = (np.exp(r * dt) - d) / (u - d)

    # Step 4: Discount factor per step
    discount = np.exp(-r * dt)

    # Step 5: Build stock prices at expiry (final nodes of the tree)
    # At step n, stock price = S * u^(n-i) * d^i  for i = 0,1,...,n
    i = np.arange(n_steps + 1)
    S_T = S * (u ** (n_steps - i)) * (d ** i)

    # Step 6: Calculate option payoff at expiry
    if option_type == 'call':
        values = np.maximum(S_T - K, 0)
    elif option_type == 'put':
        values = np.maximum(K - S_T, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Step 7: Work backwards through the tree
    # At each step, option value = discounted expected value of next step
    for _ in range(n_steps):
        values = discount * (p * values[:-1] + (1 - p) * values[1:])

    return round(values[0], 6)


def binomial_convergence(S, K, T, r, sigma, option_type='call'):
    """
    Shows how binomial tree price converges to BSM as steps increase.
    Returns prices for different step counts — useful for plotting.
    """
    step_sizes = [5, 10, 25, 50, 100, 200, 500]
    prices = []

    for n in step_sizes:
        price = binomial_tree(S, K, T, r, sigma, option_type, n_steps=n)
        prices.append(price)

    return step_sizes, prices
