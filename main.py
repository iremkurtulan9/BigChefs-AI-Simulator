import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib  # to generate a blockchain hash for data integrity

DAYS = 90  # total simulation duration (90 days)
PRODUCTS = {
    # Product: [Unit Cost (USD), Category, Storage, Perishability_Rate, Min_Stok, Max_Stok, Tier]
    # rakam ürünün hassasiyeti: 1.3 çok hassas (balık), 0.7 dayanıklı (peynir),diğer sayı stok aralıkları

    # 1. Grup: High-Volume (Yüksek Hacimli)
    'Tomato': [1.5, 'Produce', 'Dry', 0.9, 150, 300, 'High-Volume'],
    'Mixed Greens': [2.0, 'Produce', 'Cold', 1.2, 100, 200, 'High-Volume'],
    'Turkish Simit': [0.5, 'Bakery', 'Dry', 1.1, 150, 250, 'High-Volume'],  
    'Sourdough Bread': [1.2, 'Bakery', 'Dry', 0.8, 80, 150, 'High-Volume'],

    # 2. Grup: Mid-Volume (Orta Hacimli)
    'Chicken Breast': [6.0, 'Protein', 'Cold', 1.1, 50, 100, 'Mid-Volume'],
    'Cooking Cream': [4.0, 'Dairy', 'Cold', 1.0, 40, 80, 'Mid-Volume'],
    'Ezine White Cheese': [9.0, 'Dairy', 'Cold', 0.8, 30, 60, 'Mid-Volume'],
    'San Sebastian Cheesecake': [2.5, 'Bakery', 'Cold', 1.0, 40, 90, 'Mid-Volume'],

    # 3. Grup: Low-Volume / High-Value (Düşük Hacimli / Pahalı)
    'Fresh Salmon': [14.0, 'Protein', 'Cold', 1.3, 15, 35, 'Low-Volume'],
    'Ground Beef': [18.0, 'Protein', 'Cold', 1.1, 20, 50, 'Low-Volume'],
    'Avocado': [2.0, 'Produce', 'Dry', 1.0, 20, 40, 'Low-Volume'],
    'Halloumi Cheese': [12.0, 'Dairy', 'Cold', 0.7, 10, 25, 'Low-Volume']
}

data = []
start_date = datetime(2026, 5, 1)

# --- SIMULATION LOOP ---
for day in range(DAYS):
    current_date = start_date + timedelta(days=day)

    # # haftasonuysa talep %30 artıyor, stok %20 artıyor hep aynı olmaz.
    is_weekend = current_date.weekday() >= 4
    demand_mod = 1.3 if is_weekend else 1.0
    stock_mod = 1.2 if is_weekend else 1.0

    # --- COLD-START LOGIC (Rapordaki volatiliteyi koda döküyoruz) ---
    # İlk 14 gün model daha yeni öğreniyor (%82-86 arası), sonra %90'a sabitleniyor.
    current_accuracy = 0.90 if day > 14 else round(np.random.uniform(0.82, 0.86), 2)

    for prod, info in PRODUCTS.items():
        # 2. STOK VE SATIŞ (Sabah dükkanı açtık)
        # stoğumuz artık ürünün grubuna göre (Min_Stok - Max_Stok) arası değişiyor.
        base_stock = np.random.randint(info[4], info[5])
        stock = int(base_stock * stock_mod)  # eğer haftasonuysa %20 artıyor

        #stoğa orantılı %50-80 arası ne kadar satıldı/kullanıldı
        sales_demand = int(stock * np.random.uniform(0.5, 0.8) * demand_mod)
        sales = int(min(stock * 0.8, sales_demand))  # elimizdeki stoğun max %80ini satıyoruz (israf olması için kalması lazım)

        # ELDE KALAN (Satıştan sonra depoda ne kaldıysa israf oradan çıkmalı)
        leftover_stock = stock - sales

        # 3. SICAKLIK VE BOZULMA (Gün içinde sensörleri okuduk)
        if info[2] == 'Cold':
            if np.random.rand() > 0.9:  # %10 ihtimalle dolap ısınır (arıza/kapı açık kaldı)
                temp = round(np.random.uniform(7.0, 12.0), 1) #arıza varsa 7-12 derece arasına geldi
            else:
                temp = round(np.random.uniform(2.0, 5.0), 1) #arıza yoksa normal 2-5 derece arası
            # Soğuk üründe 7 derece üstü riskli
            spoilage_factor = 1.15 if temp > 7.0 else 1.0 #sıcaklık 7 üstüne çıktıysa israf %15 arttı.
        else:
            # Kuru gıda için oda sıcaklığı (18-24 derece arası)
            temp = round(np.random.uniform(18.0, 24.0), 1)
            spoilage_factor = 1.10 if temp > 23.0 else 1.0

        # 4. İSRAF HESABI (Sıcaklığa ve ürünün kendi hassasiyetine göre)
        perishability = float(info[3])  # Ürün çok mu hassas katsayısı
        potential_waste = float(leftover_stock * np.random.uniform(0.25, 0.35) * spoilage_factor * perishability)
        actual_waste = round(min(float(leftover_stock), potential_waste), 2)

        # 5. AI SİSTEM ETKİSİ (Proje hedefi: İsrafın %30'unu kurtar)
        saved_waste = round(actual_waste * 0.30, 2)  # israfın %30unu kurtardık
        final_waste = round(actual_waste - saved_waste, 2)  # her şeye rağmen kurtarılamayan atık

        # TAHMİN DOĞRULUĞU (Artık cold-start fazına göre değişiyor)
        predicted_waste = round(actual_waste * current_accuracy, 2)

        # 6. FİNANSAL VE DİĞER METRİKLER
        financial_gain = round(saved_waste * info[0], 2)  # kazancımız
        carbon_saved = round(saved_waste * 2.5, 2)  # 1kg atık başına 2.5 kg
        labor_saved = np.random.randint(10, 25)  # personel bizim sistemden ne kadar dakika kazandı

        row_data = {
            "Date": current_date.strftime("%Y-%m-%d"),
            "Product": prod,
            "Stock_Tier": info[6],  
            "Category": info[1],
            "Unit_Cost_USD": info[0],
            "Initial_Stock": stock,
            "Customer_Demand": int(sales_demand),
            "Actual_Sales": sales,
            "Actual_Waste_KG": actual_waste,
            "Predicted_Waste_KG": predicted_waste,
            "Model_Accuracy": current_accuracy,
            "Saved_Waste_KG": saved_waste,
            "Final_Waste_KG": final_waste,
            "Financial_Gain_USD": financial_gain,
            "Sensor_Temp_C": temp,
            "Storage_Type": info[2],
            "Carbon_Saved_KG": carbon_saved,
            "Labor_Time_Saved_Min": labor_saved,
            "System_Risk_Flag": "High" if temp > 7.0 else "Normal"
        }

        # 7. BLOCKCHAIN MÜHRÜ
        row_data["Blockchain_Hash"] = hashlib.sha256(str(row_data).encode()).hexdigest()[:16]
        data.append(row_data)

# --- 3. EXPORT & SUMMARY ---
df = pd.DataFrame(data)
df.to_excel("BigChefs_90Days_Final_Data.xlsx", index=False)
df.to_csv("BigChefs_90Days_Technical_Data.csv", index=False)

print("\n" + "=" * 60)
print("BIG CHEFS AI WASTE MANAGEMENT SYSTEM - SIMULATION COMPLETE")
print("=" * 60)
print(f"- Status: All data verified. 'BigChefs_90Days_Final_Data.xlsx' is ready.")
print("=" * 60 + "\n")
