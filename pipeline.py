
import pandas as pd
import yfinance as yf
import requests

# ========= ROPA =========

oil = yf.Ticker("BZ=F").history(period="3mo")

df_oil = pd.DataFrame({
    "date": pd.to_datetime(oil.reset_index().iloc[:, 0]).dt.tz_localize(None),
    "price_brent": oil.reset_index().iloc[:, 4].astype(float)
})

# ========= USD =========

url = "http://api.nbp.pl/api/exchangerates/rates/A/USD/last/60/?format=json"
data = requests.get(url).json()

df_fx = pd.DataFrame([
    {"date": item["effectiveDate"], "usd_pln": item["mid"]}
    for item in data["rates"]
])

df_fx["date"] = pd.to_datetime(df_fx["date"]).dt.tz_localize(None)

# ========= MERGE =========

df = pd.merge(df_oil, df_fx, on="date", how="left")

df = df.sort_values("date")
df["price_brent"] = df["price_brent"].ffill()
df["usd_pln"] = df["usd_pln"].ffill()

# cena ropy w PLN
df["oil_pln"] = df["price_brent"] * df["usd_pln"]

# ========= SAVE =========

df.to_csv("data.csv", index=False)

print("✅ data.csv updated!")
