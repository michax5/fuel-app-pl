
import pandas as pd
import yfinance as yf
import requests


# ========= ROPA =========

oil = yf.Ticker("BZ=F").history(period="3mo")

df_oil = oil.reset_index()

# 💥 WYMUSZENIE NORMALNYCH KOLUMN
df_oil.columns = [str(col) for col in df_oil.columns]

# wybór kolumn po nazwie string
df_oil = df_oil.rename(columns={
    "Date": "date",
    "Close": "price_brent"
})

df_oil = df_oil[["date", "price_brent"]]
df_oil["date"] = pd.to_datetime(df_oil["date"])



# ========= USD =========
url = "http://api.nbp.pl/api/exchangerates/rates/A/USD/last/60/?format=json"
res = requests.get(url)
data = res.json()

df_fx = pd.DataFrame([
    {"date": item["effectiveDate"], "usd_pln": item["mid"]}
    for item in data["rates"]
])
df_fx["date"] = pd.to_datetime(df_fx["date"])

#test


print("df_oil columns:", df_oil.columns)
print(type(df_oil.columns))



# ========= MERGE =========
df = pd.merge(df_oil[["date", "price_brent"]], df_fx, on="date", how="left")

df = df.sort_values("date")
df["price_brent"] = df["price_brent"].ffill()
df["usd_pln"] = df["usd_pln"].ffill()

df["oil_pln"] = df["price_brent"] * df["usd_pln"]

# ========= SAVE =========
df.to_csv("data.csv", index=False)

print("✅ data.csv updated!")
print("df_oil columns:", df_oil.columns)
print("df_fx columns:", df_fx.columns)
