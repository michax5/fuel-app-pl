
print("🔥 FINAL PIPELINE")

import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import re

# =========================
# 1. ROPA + USD
# =========================

oil = yf.Ticker("BZ=F").history(period="3mo")
df_oil = pd.DataFrame({
    "date": pd.to_datetime(oil.reset_index().iloc[:, 0]).dt.tz_localize(None),
    "price_brent": oil.reset_index().iloc[:, 4].astype(float)
})

df_oil["date"] = pd.to_datetime(df_oil["date"]).dt.tz_localize(None)

# USD
url = "http://api.nbp.pl/api/exchangerates/rates/A/USD/last/60/?format=json"
data = requests.get(url).json()

df_fx = pd.DataFrame([
    {"date": item["effectiveDate"], "usd_pln": item["mid"]}
    for item in data["rates"]
])
df_fx["date"] = pd.to_datetime(df_fx["date"]).dt.tz_localize(None)

# merge oil + fx
df = pd.merge(df_oil, df_fx, on="date", how="left")
df = df.sort_values("date")

df["price_brent"] = df["price_brent"].ffill()
df["usd_pln"] = df["usd_pln"].ffill()

df["oil_pln"] = df["price_brent"] * df["usd_pln"]

# =========================
# 2. PB95 (Monitor Polski – BEZ SELENIUM)
# =========================

search_url = "https://monitorpolski.gov.pl/szukaj?pSize=20&pNumber=1&sKey=year&title=maksymalnej+ceny+paliw"

resp = requests.get(search_url)
soup = BeautifulSoup(resp.text, "html.parser")

pdf_links = []

for a in soup.find_all("a", href=True):
    if "/MP/" in a["href"] and "pozycja" in a["href"]:
        page_url = "https://monitorpolski.gov.pl" + a["href"]

        try:
            r = requests.get(page_url)
            s = BeautifulSoup(r.text, "html.parser")

            for link in s.find_all("a", href=True):
                if link["href"].endswith(".pdf"):
                    pdf_links.append("https://monitorpolski.gov.pl" + link["href"])
        except:
            continue

pdf_links = list(set(pdf_links))

data_pb = []

for pdf_url in pdf_links[:5]:  # ograniczamy (ważne!)
    try:
        r = requests.get(pdf_url)
        pdf_file = io.BytesIO(r.content)

        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()

        matches = re.findall(r'(\d+,\d+)\s*zł\s*za\s*1\s*l', text)

        if len(matches) >= 1:
            pb95 = float(matches[0].replace(",", "."))

            # data
            date_match = re.search(r'dnia (\d{1,2} \w+ \d{4})', text)

            if date_match:
                date_str = date_match.group(1)

                months = {
                    "stycznia": "January",
                    "lutego": "February",
                    "marca": "March",
                    "kwietnia": "April",
                    "maja": "May",
                    "czerwca": "June",
                    "lipca": "July",
                    "sierpnia": "August",
                    "września": "September",
                    "października": "October",
                    "listopada": "November",
                    "grudnia": "December"
                }

                for pl, en in months.items():
                    date_str = date_str.replace(pl, en)

                date = pd.to_datetime(date_str, errors="coerce")

                data_pb.append({
                    "date": date,
                    "pb95": pb95
                })

    except:
        continue

df_pb = pd.DataFrame(data_pb)

if not df_pb.empty:
    df_pb["date"] = pd.to_datetime(df_pb["date"]) + pd.Timedelta(days=1)
    df_pb = df_pb.sort_values("date")

    df_pb = df_pb.set_index("date").resample("D").ffill().reset_index()

    # =========================
    # MERGE PB95
    # =========================
    df = pd.merge(df, df_pb[["date", "pb95"]], on="date", how="left")
    df["pb95"] = df["pb95"].ffill()

# =========================
# 3. MODEL (LAG)
# =========================

df["oil_pln_lag3"] = df["oil_pln"].shift(3)

# =========================
# 4. SAVE
# =========================

df.to_csv("data.csv", index=False)

print("✅ data.csv updated with pb95 + oil")
``
