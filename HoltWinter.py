import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Fungsi untuk menghitung MA, CMA, Forecast, MSE, dan MAPE
def calculate_forecasting(data, period_type):
    # Menentukan kolom moving average (MA dengan window 4)
    data['MA'] = data['Aktual'].rolling(window=4, center=False).mean()
    
    # Menentukan CMA (Centered Moving Average)
    data['CMA'] = data['MA'].rolling(window=2, center=True).mean()

    # Menentukan komponen tren (T)
    data['T'] = np.linspace(1, len(data), len(data))
    
    # Seasonal Index (contoh: dummy, bisa disesuaikan)
    data['SI'] = data['Aktual'] / data['CMA']
    
    # Forecast (contoh: sederhana)
    data['Forecast'] = data['CMA'] * data['SI'].mean()

    # Error calculation
    data['Error'] = data['Aktual'] - data['Forecast']
    data['Error^2'] = data['Error'] ** 2
    data['Abs(Error/Aktual)'] = np.abs(data['Error'] / data['Aktual'])

    # MSE dan MAPE
    mse = data['Error^2'].mean()
    mape = (data['Abs(Error/Aktual)'].mean()) * 100

    return data, mse, mape

# Streamlit Interface
st.title("Forecasting HoltWinter dengan CRUD")
st.write("Aplikasi sederhana untuk forecasting dengan metode HoltWinter.")

# Input data
period_type = st.selectbox("Pilih Tipe Periode:", ['Tahun', 'Kwartal'])
uploaded_file = st.file_uploader("Upload File Data (CSV)", type=['csv'])

if 'data' not in st.session_state:
    st.session_state.data = None  # Untuk menyimpan data yang di-upload atau dimodifikasi

if uploaded_file:
    # Load data dengan delimiter ";"
    df = pd.read_csv(uploaded_file, sep=";")

    # Menghapus spasi ekstra dan memastikan nama kolom huruf kecil
    df.columns = df.columns.str.strip().str.lower()

    # Ubah nama kolom ke format yang diharapkan (Tahun, Periode, Aktual)
    rename_columns = {'tahun': 'Tahun', 'periode': 'Periode', 'aktual': 'Aktual'}
    df.rename(columns=rename_columns, inplace=True)

    # Tambahkan kolom checkbox untuk menghapus baris
    df['Hapus'] = False

    # Simpan data ke session_state
    st.session_state.data = df

if st.session_state.data is not None:
    # Menggunakan data editor untuk edit langsung pada tabel
    df = st.session_state.data
    st.write("Data yang Dimuat (Edit Langsung di Tabel):")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # Update data jika ada perubahan
    st.session_state.data = edited_df

    # Tampilkan tombol untuk menghapus data yang dicentang
    if st.button("Hapus Data yang Dipilih"):
        df = st.session_state.data
        st.session_state.data = df[df['Hapus'] == False].reset_index(drop=True)
        st.success("Data yang dicentang berhasil dihapus.")

    # Menampilkan data setelah modifikasi
    st.write("Data Setelah Modifikasi:")
    st.write(st.session_state.data)

    # Tombol untuk memproses forecasting ulang
    if st.button("Proses Forecasting"):
        # Jika periode adalah Kwartal, kita perlu memproses data untuk kuartal
        if period_type == 'Kwartal':
            # Mengelompokkan data berdasarkan tahun dan kuartal
            df['Kuartal'] = (df['Periode'] - 1) // 3 + 1  # Menghitung kuartal
            df['Periode'] = df['Tahun'].astype(str) + ' Q' + df['Kuartal'].astype(str)  # Format periode kuartal
            df = df.groupby(['Tahun', 'Kuartal'], as_index=False).agg({'Aktual': 'sum'})  # Menghitung total aktual per kuartal

        result, mse, mape = calculate_forecasting(df, period_type)

        # Menampilkan hasil
        st.subheader("Hasil Forecasting:")
        st.write(result)

        # Menampilkan MSE dan MAPE
        st.write(f"Mean Squared Error (MSE): {mse:.2f}")
        st.write(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")

        # Visualisasi
        st.subheader("Grafik Forecasting")
        plt.figure(figsize=(10, 5))
        plt.plot(result['Periode'], result['Aktual'], label="Aktual")
        plt.plot(result['Periode'], result['Forecast'], label="Forecast", linestyle="--")
        plt.legend()
        st.pyplot(plt)