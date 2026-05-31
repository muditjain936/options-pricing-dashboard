import streamlit as st
import numpy as np
import plotly.graph_objects as go
from pricing import (
    black_scholes, implied_volatility,
    calculate_greeks,
    monte_carlo_price,
    binomial_tree, binomial_convergence
)

st.set_page_config(page_title="Options Pricing Dashboard", page_icon="📈", layout="wide")
st.title("📈 Options Pricing & Greeks Dashboard")
st.markdown("*Black-Scholes · Monte Carlo · Binomial Tree · Greeks · Vol Surface*")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.header("Contract Parameters")
S     = st.sidebar.slider("Spot Price (S)",         10.0, 500.0, 100.0, 1.0)
K     = st.sidebar.slider("Strike Price (K)",        10.0, 500.0, 100.0, 1.0)
T     = st.sidebar.slider("Time to Expiry (years)",  0.01,   3.0,   0.5, 0.01)
r     = st.sidebar.slider("Risk-Free Rate (%)",       0.0,  15.0,   5.0, 0.1) / 100
sigma = st.sidebar.slider("Volatility σ (%)",         1.0, 100.0,  20.0, 0.5) / 100
option_type = st.sidebar.radio("Option Type", ["call", "put"])

st.sidebar.divider()
moneyness = S / K
if moneyness > 1.02:
    st.sidebar.success(f"ITM — S/K = {moneyness:.3f}")
elif moneyness < 0.98:
    st.sidebar.error(f"OTM — S/K = {moneyness:.3f}")
else:
    st.sidebar.warning(f"ATM — S/K = {moneyness:.3f}")

# ── Core calculations (fast) ──────────────────────────────────
bsm_price  = black_scholes(S, K, T, r, sigma, option_type)
greeks     = calculate_greeks(S, K, T, r, sigma, option_type)
bin_price  = binomial_tree(S, K, T, r, sigma, option_type)
intrinsic  = max(S - K, 0) if option_type == 'call' else max(K - S, 0)
time_value = bsm_price - intrinsic

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Pricing", "🔢 Greeks", "📊 Payoff", "🌐 Vol Surface", "🎲 Monte Carlo"
])

# ── TAB 1 : PRICING ───────────────────────────────────────────
with tab1:
    st.subheader("Model Comparison")
    col1, col2, col3 = st.columns(3)
    col1.metric("Black-Scholes", f"${bsm_price:.4f}", "Reference")
    col2.metric("Binomial Tree", f"${bin_price:.4f}", f"{bin_price - bsm_price:+.4f}")
    col3.metric("Intrinsic Value", f"${intrinsic:.4f}")

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Time Value", f"${time_value:.4f}")
    col2.metric("Total (BSM)", f"${bsm_price:.4f}")

    st.divider()
    st.subheader("Binomial Tree Convergence to BSM")
    steps, prices = binomial_convergence(S, K, T, r, sigma, option_type)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=steps, y=prices, mode='lines+markers',
                             name='Binomial', line=dict(color='green', width=2)))
    fig.add_hline(y=bsm_price, line_dash="dash", line_color="blue",
                  annotation_text="BSM Price")
    fig.update_layout(xaxis_title="Number of Steps", yaxis_title="Option Price ($)",
                      height=350, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 2 : GREEKS ────────────────────────────────────────────
with tab2:
    st.subheader("Option Greeks")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Δ Delta", f"{greeks['delta']:.4f}", "∂P/∂S")
    col2.metric("Γ Gamma", f"{greeks['gamma']:.4f}", "∂²P/∂S²")
    col3.metric("ν Vega",  f"{greeks['vega']:.4f}",  "∂P/∂σ per 1%")
    col4.metric("Θ Theta", f"{greeks['theta']:.4f}", "∂P/∂t per day")
    col5.metric("ρ Rho",   f"{greeks['rho']:.4f}",   "∂P/∂r per 1%")

    st.divider()
    st.subheader("Delta & Gamma vs Spot Price")
    spots  = np.linspace(S * 0.5, S * 1.5, 100)
    deltas = [calculate_greeks(s, K, T, r, sigma, option_type)['delta'] for s in spots]
    gammas = [calculate_greeks(s, K, T, r, sigma, option_type)['gamma'] for s in spots]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=spots, y=deltas, name='Delta',
                             line=dict(color='royalblue', width=2)))
    fig.add_trace(go.Scatter(x=spots, y=gammas, name='Gamma',
                             line=dict(color='orange', width=2), yaxis='y2'))
    fig.add_vline(x=S, line_dash="dash", line_color="white",
                  annotation_text="Current S")
    fig.update_layout(
        xaxis_title="Spot Price", yaxis_title="Delta",
        yaxis2=dict(title="Gamma", overlaying='y', side='right'),
        height=380, template="plotly_dark", legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 3 : PAYOFF ────────────────────────────────────────────
with tab3:
    st.subheader("Payoff Diagram at Expiry")
    spots   = np.linspace(S * 0.5, S * 1.5, 200)
    payoffs = [max(s - K, 0) if option_type == 'call' else max(K - s, 0) for s in spots]
    pnl     = [p - bsm_price for p in payoffs]
    breakeven = K + bsm_price if option_type == 'call' else K - bsm_price

    col1, col2, col3 = st.columns(3)
    col1.metric("Breakeven",  f"${breakeven:.2f}")
    col2.metric("Max Loss",   f"-${bsm_price:.4f}")
    col3.metric("Max Profit", "Unlimited" if option_type == 'call' else f"${K - bsm_price:.2f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=spots, y=pnl, fill='tozeroy',
                             name='P&L', line=dict(color='limegreen', width=2)))
    fig.add_hline(y=0, line_color='white', line_width=1)
    fig.add_vline(x=breakeven, line_dash='dash', line_color='yellow',
                  annotation_text=f"Breakeven ${breakeven:.2f}")
    fig.update_layout(xaxis_title="Stock Price at Expiry", yaxis_title="P&L ($)",
                      height=400, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 4 : VOL SURFACE ───────────────────────────────────────
with tab4:
    st.subheader("Implied Volatility Surface")
    strikes  = np.linspace(S * 0.7, S * 1.3, 15)
    expiries = np.linspace(0.1, 2.0, 15)
    K_grid, T_grid = np.meshgrid(strikes, expiries)
    moneyness_grid = np.log(K_grid / S)
    iv_surface = sigma * (1 + 0.15 * moneyness_grid**2 / T_grid
                            - 0.05 * moneyness_grid / T_grid) \
                       * np.maximum(0.8, 1 + 0.1 / np.sqrt(T_grid))
    fig = go.Figure(data=[go.Surface(
        x=strikes, y=expiries, z=iv_surface * 100,
        colorscale='Blues', colorbar=dict(title='IV (%)')
    )])
    fig.update_layout(
        scene=dict(xaxis_title='Strike', yaxis_title='Expiry (years)',
                   zaxis_title='Implied Vol (%)'),
        height=500, template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Vol smile: OTM options carry higher IV due to demand for tail hedges")

# ── TAB 5 : MONTE CARLO ───────────────────────────────────────
with tab5:
    st.subheader("Monte Carlo Simulation")
    st.info("Click the button below to run Monte Carlo (takes a few seconds)")

    if st.button("▶ Run Monte Carlo (10,000 paths)"):
        with st.spinner("Simulating GBM paths..."):
            mc_result = monte_carlo_price(S, K, T, r, sigma, option_type,
                                          n_simulations=10000)
        mc_price = mc_result['price']
        mc_se    = mc_result['std_error']
        paths    = mc_result['price_paths']

        col1, col2, col3 = st.columns(3)
        col1.metric("MC Price",  f"${mc_price:.4f}")
        col2.metric("BSM Price", f"${bsm_price:.4f}")
        col3.metric("Std Error", f"±${mc_se:.4f}")

        t_axis = np.linspace(0, T, paths.shape[1])
        fig = go.Figure()
        for i in range(min(100, len(paths))):
            fig.add_trace(go.Scatter(
                x=t_axis, y=paths[i], mode='lines',
                line=dict(width=0.5, color='rgba(24,95,165,0.15)'),
                showlegend=False
            ))
        fig.add_hline(y=K, line_dash='dash', line_color='red',
                      annotation_text=f"Strike K={K}")
        fig.update_layout(xaxis_title="Time (years)", yaxis_title="Stock Price",
                          height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        payoffs_mc = np.maximum(paths[:, -1] - K, 0) if option_type == 'call' \
                     else np.maximum(K - paths[:, -1], 0)
        fig2 = go.Figure(data=[go.Histogram(
            x=payoffs_mc, nbinsx=50,
            marker_color='steelblue', opacity=0.8
        )])
        fig2.update_layout(xaxis_title="Payoff ($)", yaxis_title="Frequency",
                           height=350, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)