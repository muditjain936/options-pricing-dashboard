import numpy as np
from scipy.stats import norm

def calculate_greeks(S, K, T, r, sigma, option_type='call'):
    """
    Calculates all 5 Greeks for a European option.

    Delta : How much the option price moves per $1 move in stock
    Gamma : How much Delta itself changes per $1 move in stock
    Vega  : How much price changes per 1% move in volatility
    Theta : How much price decays per 1 day passing
    Rho   : How much price changes per 1% move in interest rate
    """

    # Step 1: Calculate d1 and d2 (same as BSM formula)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Step 2: Standard normal PDF and CDF values
    pdf_d1 = norm.pdf(d1)       # n(d1) — used in Gamma, Vega, Theta
    cdf_d1 = norm.cdf(d1)       # N(d1)
    cdf_d2 = norm.cdf(d2)       # N(d2)

    # Step 3: Calculate each Greek
    if option_type == 'call':
        delta = cdf_d1
        rho   = K * T * np.exp(-r * T) * cdf_d2 / 100

        theta = (
            (-S * pdf_d1 * sigma) / (2 * np.sqrt(T))
            - r * K * np.exp(-r * T) * cdf_d2
        ) / 365  # divide by 365 to get per-day decay

    elif option_type == 'put':
        delta = cdf_d1 - 1
        rho   = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

        theta = (
            (-S * pdf_d1 * sigma) / (2 * np.sqrt(T))
            + r * K * np.exp(-r * T) * norm.cdf(-d2)
        ) / 365

    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Gamma and Vega are same for both call and put
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega  = S * pdf_d1 * np.sqrt(T) / 100  # per 1% vol change

    return {
        'delta': round(delta, 6),
        'gamma': round(gamma, 6),
        'vega' : round(vega,  6),
        'theta': round(theta, 6),
        'rho'  : round(rho,   6)
    }