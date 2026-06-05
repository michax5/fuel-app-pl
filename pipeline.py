
import pandas as pd
import yfinance as yf
import requests

# ========= ROPA =========


oil = yf.download("BZ=F", period="3mo")

# 🔥 reset index
df_oil = oil.reset_index()

# 🔥 bierzemy wartości (unikamy MultiIndex)
df_oil["price_brent"] = oil["Close"].to_numpy()

# data
df_oil["date"] = pd.to_datetime(df_oil["Date"])

# finalny dataframe
df_oil = df_oil[["date", "price_brent"]]


# ========= USD =========
url = "http://api.nbp.pl/api/exchangerates/rates/A/USD/last/60/?format=json"
res = requests.get(url)
data = res.json()

df_fx = pd.DataFrame([
    {"date": item["effectiveDate"], "usd_pln": item["mid"]}
    for item in data["rates"]
])
df_fx["date"] = pd.to_datetime(df_fx["date"])

# ========= MERGE =========
df = pd.merge(df_oil[["date", "price_brent"]], df_fx, on="date", how="left")

df = df.sort_values("date")
df["price_brent"] = df["price_brent"].ffill()
df["usd_pln"] = df["usd_pln"].ffill()

df["oil_pln"] = df["price_brent"] * df["usd_pln"]

# ========= SAVE =========
df.to_csv("data.csv", index=False)

print("✅ data.csv updated!")
