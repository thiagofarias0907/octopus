import streamlit as st
import datetime as dt

conn = st.connection("postgresql")
df = conn.query("""
    SELECT 
        DATE(extraction_datetime) as "Data",
        name as "Nome",
        raw_material_cost as "Costo Materia Prima",
        commercial_cost as "Costo Commercializzazione",
        time_rate_type as "Tipo Tariffa",
        user_type as "Tipo di Utenze"         
    FROM plan_offer;
    
""", ttl="5m")

st.title("Visualizzazione delle offerte e tariffe")

date_input = st.date_input("Selezione la data:", dt.date.today())
st.write("Giorno in cui è stato applicato il filtro:", date_input)

filtered_df = df[df['Data'] == date_input]

st.dataframe(data=filtered_df)