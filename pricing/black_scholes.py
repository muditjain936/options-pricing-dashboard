import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    S     : Current stock price
    K     : Strike price
    T     : Time to expiry (in years)
    r     : Risk-free rate (e.g. 0.05)
    sigma : Volatility (e.g. 0.20)
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price


def implied_volatility(market_price, S, K, T, r, option_type='call'):
    """
    Finds the implied volatility using Brent's root-finding method.
    """
    from scipy.optimize import brentq

    def objective(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - market_price

    try:
        iv = brentq(objective, 1e-4, 5.0)
        return iv
    except ValueError:
        return None