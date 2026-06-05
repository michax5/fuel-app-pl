
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# ✅ ŁADOWANIE DANYCH
# =========================
df_final = pd.read_csv("data.csv")
df_final["date"] = pd.to_datetime(df_final["date"])


# =========================
# ✅ SYGNAŁ NA DZIŚ
# =========================
oil_today = df_final["oil_pln"].shift(3).iloc[-1]
oil_yesterday = df_final["oil_pln"].shift(3).iloc[-2]

change = oil_today - oil_yesterday

threshold = 5

if change > threshold:
    signal = "⛽ KUP TERAZ – ceny paliwa mogą wzrosnąć"
    color = "green"
elif change < -threshold:
    signal = "⏳ POCZEKAJ – ceny mogą spaść"
    color = "orange"
else:
    signal = "⚖️ BRAK WYRAŹNEGO SYGNAŁU"
    color = "gray"


# =========================
# ✅ UI
# =========================
st.title("⛽ Analiza rynku paliw")

# ---- SYGNAŁ ----
st.markdown("## 📊 Sygnał na dziś")
st.markdown(f"<h2 style='color:{color}'>{signal}</h2>", unsafe_allow_html=True)

# ---- DATA ----
st.write("📅 Data:", df_final["date"].iloc[-1].date())


# =========================
# ✅ WYKRES
# =========================
st.subheader("📈 Wykres cen")

fig, ax1 = plt.subplots(figsize=(10,5))

# paliwo
ax1.plot(df_final["date"], df_final["pb95"],
         label="Pb95", color="blue", linewidth=2)
ax1.set_ylabel("Pb95 (zł/l)", color="blue")

# druga oś
ax2 = ax1.twinx()

ax2.plot(df_final["date"], df_final["oil_pln"].shift(3),
         label="Ropa PLN (lag 3)", color="red", linestyle="--")

ax2.set_ylabel("Ropa PLN", color="red")

# legenda
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(lines1 + lines2, labels1 + labels2)

plt.title("Cena paliwa vs ropa (opóźnienie 3 dni)")
plt.grid()

st.pyplot(fig)


# =========================
# ✅ Korelacja
# =========================

st.subheader("📈 Korelacja (lag)")

for lag in range(0, 10):
    corr = df_final["pb95"].corr(df_final["oil_pln"].shift(lag))
    st.write(f"Lag {lag}: {corr:.3f}")



# =========================
# ✅ TABELA
# =========================
st.subheader("📋 Dane")

st.dataframe(df_final.tail(30))


# =========================
# ✅ OPIS
# =========================
st.markdown("---")
st.markdown("""
### ℹ️ Opis systemu

- zależność ropa → paliwo  
- opóźnienie ~3 dni  
- dane: Brent + USD/PLN  

👉 sygnał pokazuje kierunek zmian cen
""")
