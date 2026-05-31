import numpy as np

def monte_carlo_price(S, K, T, r, sigma, option_type='call', n_simulations=10000, n_steps=252):
    """
    Prices an option using Monte Carlo simulation.
    
    How it works:
    - Simulates thousands of possible stock price paths
    - Each path follows Geometric Brownian Motion (GBM)
    - At expiry, calculates the payoff for each path
    - Average discounted payoff = option price

    Parameters:
        S            : Current stock price
        K            : Strike price
        T            : Time to expiry (in years)
        r            : Risk-free rate
        sigma        : Volatility
        option_type  : 'call' or 'put'
        n_simulations: Number of paths to simulate (more = more accurate)
        n_steps      : Number of time steps per path (252 = trading days in a year)
    """

    # Step 1: Calculate time step size
    dt = T / n_steps

    # Step 2: Generate random shocks (Z) for all paths and steps at once
    # Shape: (n_simulations, n_steps)
    Z = np.random.standard_normal((n_simulations, n_steps))

    # Step 3: Antithetic variates — mirror each random number
    # This reduces variance and improves accuracy without more simulations
    Z = np.concatenate([Z, -Z], axis=0)  # doubles to 2 * n_simulations

    # Step 4: Calculate incremental price moves using GBM formula
    # GBM: dS = S * (r*dt + sigma*sqrt(dt)*Z)
    increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z

    # Step 5: Cumulative sum gives log-returns, then exponentiate
    log_returns = np.cumsum(increments, axis=1)
    price_paths = S * np.exp(log_returns)  # shape: (2*n_simulations, n_steps)

    # Step 6: Get final stock price at expiry (last column)
    S_T = price_paths[:, -1]

    # Step 7: Calculate payoff at expiry
    if option_type == 'call':
        payoffs = np.maximum(S_T - K, 0)   # Call: max(S_T - K, 0)
    elif option_type == 'put':
        payoffs = np.maximum(K - S_T, 0)   # Put:  max(K - S_T, 0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Step 8: Discount average payoff back to present value
    price = np.exp(-r * T) * np.mean(payoffs)

    # Step 9: Standard error tells us how accurate our estimate is
    std_error = np.std(payoffs) / np.sqrt(len(payoffs))

    return {
        'price'      : round(price, 6),
        'std_error'  : round(std_error, 6),
        'n_paths'    : len(payoffs),
        'price_paths': price_paths   # we'll use this to plot paths later
    }