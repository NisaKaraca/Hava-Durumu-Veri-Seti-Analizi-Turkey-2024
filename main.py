import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

dt = pd.read_csv("hava_durumu_tahmini (5).csv")
dt.head()

dt.columns = ["ID", "City", "Date", "Status", "Temperature (°C)"]

dt["Status"].unique()
status_dict = {
    'Orta kuvvetli yağmurlu': 'Moderate rain',
    'Bölgesel düzensiz yağmur yağışlı': 'Scattered rain',
    'Parçalı Bulutlu': 'Partly cloudy',
    'Çok bulutlu': 'Mostly cloudy',
    'Güneşli': 'Sunny',
    'Bulutlu': 'Cloudy',
    'Şiddetli yağmurlu': 'Heavy rain',
    'Orta kuvvetli karlı': 'Moderate snow',
    'Hafif sağnak şeklinde kar': 'Light snow showers',
    'Hafif karlı': 'Light snow',
    'Hafif dondurucu yağmurlu': 'Light freezing rain'
}

dt["Status"] = dt["Status"].map(status_dict)

dt["Status"].unique()
def weather_category(x):
    x = x.lower()
    if "sunny" in x:
        return "Sunny"
    elif "cloudy" in x:
        return "Cloudy"
    elif "rain" in x:
        return "Rainy"
    elif "snow" in x:
        return "Snowy"
    else:
        return "Other"

dt["Status Category"] = dt["Status"].apply(weather_category)

dt.isnull().sum() # boş verilerin sayısına bakalım
dt = dt.drop_duplicates(subset=["City", "Date"], keep="first") # Tekrar edenleri silmek için
print("Şehir sayısı:", dt["City"].nunique())
print("Tarih sayısı:", dt["Date"].nunique()) # Her tarihte tüm şehirler var mı diye kontrol edelim

check = dt.groupby("Date")["City"].nunique()
print(check)


# 2024-11-15 tarihinde 1 tane eksik tarih çıktı 2024-11-29 fazladan 1 veri var
# 2024-11-29' daki verimizi tamamen kaldıralım verimiz 2024-11-15 ile 2024-11-28 kapsayacak.
# 2024-11-15 tarihindeki eksik veri üzerine çalışalım.
dt = dt[dt["Date"] != "2024-11-29"] # 2024-11-29 kaldıralım
check = dt.groupby("Date")["City"].nunique()
print(check)
# Eksik şehri bulmak için
all_cities = set(dt["City"].unique())
cities_15 = set(dt[dt["Date"] == "2024-11-15"]["City"].unique())
missing_city = list(all_cities - cities_15)
print("Eksik şehir:", missing_city)
if missing_city:
    missing_row = dt[(dt["City"] == missing_city[0])].iloc[0].copy()  # diğer günden örnek alıyoruz
    missing_row["Date"] = "2024-11-15"  # tarihi 2024-11-15 yap
    dt = pd.concat([dt, pd.DataFrame([missing_row])], ignore_index=True)

check = dt.groupby("Date")["City"].nunique()
print(check)

dt.info()  # kolonların type bakıyoruz

# Date kolonunun veri tipi şu anda object, ama ben gün, ay ve yıl olarak yeni kolonlar oluşturmak istediğim için
# öncelikle Date kolonunu datetime formatına çevireceğim
dt["Date"] = pd.to_datetime(dt["Date"], errors = "coerce")
dt.info()

dt["Day"] = dt["Date"].dt.day
dt["Month"] = dt["Date"].dt.month
dt["Year"] = dt["Date"].dt.year
dt.head()


# 15-28 Kasım 2024 Tarihleri Arasında Türkiye’de Şehirlerin Ortalama Sıcaklık Dağılımı
city_avg_temp = dt.groupby("City")["Temperature (°C)"].mean().reset_index()
city_avg_temp = city_avg_temp.sort_values(by="Temperature (°C)", ascending=False)

plt.figure(figsize=(12,6))
plt.bar(city_avg_temp["City"], city_avg_temp["Temperature (°C)"], color="skyblue")
plt.xticks(rotation=90)
plt.xlabel("Şehir")
plt.ylabel("15 Günlük Ortalama Sıcaklık (°C)")
plt.title("Türkiye'de Şehirlerin 15 Günlük Ortalama Sıcaklıkları")
plt.tight_layout()
plt.show()

# 15 Kasım- 28 Kasım 2024 Arası Ortalama En Soğuk 5 Şehir ile Ortalama En Sıcak 5 Şehir
city_avg = dt.groupby("City")["Temperature (°C)"].mean().reset_index()
hottest_5 = city_avg.sort_values(by="Temperature (°C)", ascending=False).head(5)
coldest_5 = city_avg.sort_values(by="Temperature (°C)", ascending=True).head(5)

plt.figure(figsize=(12,6))
sns.barplot(x="City", y="Temperature (°C)", data=coldest_5, color="skyblue", label="En Soğuk")
sns.barplot(x="City", y="Temperature (°C)", data=hottest_5, color="orange", label="En Sıcak")

plt.title("En Sıcak 5 Şehir vs En Soğuk 5 Şehir (15 Günlük Ortalama Sıcaklık)")
plt.xlabel("Şehir")
plt.ylabel("Ortalama Sıcaklık (°C)")
plt.legend()

for p in plt.gca().patches:
    plt.gca().annotate(f'{p.get_height():.1f}°C',
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='bottom')

plt.show()

# 15-28 Kasım 2024: Türkiye Genelinde Günlük Ortalama Sıcaklık ve Standart Sapma
daily_stats = dt.groupby("Date")["Temperature (°C)"].agg(["mean", "std"]).reset_index()

fig, ax1 = plt.subplots(figsize=(10,6))
ax1.plot(daily_stats["Date"], daily_stats["mean"], marker="o", color="blue", label="Ortalama Sıcaklık")
ax1.set_xlabel("Tarih")
ax1.set_ylabel("Ortalama Sıcaklık (°C)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")

ax2 = ax1.twinx()
ax2.plot(daily_stats["Date"], daily_stats["std"], marker="s", color="red", label="Standart Sapma")
ax2.set_ylabel("Standart Sapma (°C)", color="red")
ax2.tick_params(axis="y", labelcolor="red")

plt.title("Türkiye Genelinde Günlük Ortalama Sıcaklık ve Standart Sapma")
fig.tight_layout()
plt.show()

print(daily_stats)

# 15-28 Kasım 2024: Türkiye’de Günlük Hava Durumu Dağılımı
daily_category = dt.groupby(["Date", "Status Category"])["City"].nunique().reset_index()
daily_pivot = daily_category.pivot(index="Date", columns="Status Category", values="City").fillna(0)

colors = {
    "Cloudy": "gray",
    "Rainy": "royalblue",
    "Snowy": "silver",
    "Sunny": "orange"
}
ax = daily_pivot.plot(
    kind="bar",
    stacked=True,
    figsize=(12,6),
    color=[colors[cat] for cat in daily_pivot.columns]
)
ax.set_xticks(range(len(daily_pivot)))
ax.set_xticklabels(daily_pivot.index.strftime("%y-%m-%d"), rotation=45)


for i in range(len(daily_pivot)):
    y_offset = 0
    for category in daily_pivot.columns:
        value = daily_pivot.iloc[i][category]
        if value > 0:
            ax.text(
                i,
                y_offset + value/2,
                int(value),
                ha='center',
                va='center',
                fontsize=9,
                color='black'
            )
            y_offset += value

plt.xlabel("Tarih")
plt.ylabel("İl Sayısı")
plt.title("Türkiye'de Günlük Hava Durumu Dağılımı")
plt.xticks(rotation=45)
plt.legend(title="Durum Kategorisi")
plt.tight_layout()
plt.show()


# 15-28 Kasım 2024 Hava Durumu Kategorilerine Göre Sıcaklık Dağılımı
plt.figure(figsize=(12,6))
colors = {
    "Cloudy": "gray",
    "Rainy": "royalblue",
    "Snowy": "silver",
    "Sunny": "orange"
}
sns.violinplot(
    x="Status Category",
    y="Temperature (°C)",
    hue="Status Category",
    data=dt,
    palette=colors,
    legend=False
)
plt.title("Hava Durumu Kategorisine Göre Sıcaklık Dağılımı")
plt.xlabel("Hava Durumu Kategorisi")
plt.ylabel("Sıcaklık (°C)")
plt.show()


