import pandas as pd


class TALIBWrapper:
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        prices = pd.to_numeric(prices, errors="coerce").dropna()
        if prices.empty or len(prices) < period:
            return 0.0
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 0.0

    def calculate_ema(self, prices: pd.Series, period: int = 20) -> float:
        prices = pd.to_numeric(prices, errors="coerce").dropna()
        if prices.empty:
            return 0.0
        return float(prices.ewm(span=period, adjust=False).mean().iloc[-1])

    def get_all_indicators(self, df):
        if df.empty or "Close" not in df:
            return {"RSI_14": 0.0, "EMA_20": 0.0}
        return {"RSI_14": self.calculate_rsi(df["Close"]), "EMA_20": self.calculate_ema(df["Close"])}
