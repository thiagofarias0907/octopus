import streamlit as st
import datetime as dt

conn = st.connection("postgresql")

st.title("Visualizzazione delle offerte e tariffe")

date_input = st.date_input("Selezione la data:", dt.date.today())
st.write("Giorno in cui è stato applicato il filtro:", date_input)

if date_input is not None:
    df = conn.query(f"""
        SELECT 
            DATE(extraction_datetime) as "Data",
            name as "Nome",
            raw_material_cost as "Costo Materia Prima",
            commercial_cost as "Costo Commercializzazione",
            time_rate_type as "Tipo Tariffa",
            user_type as "Tipo di Utenze"         
        FROM plan_offer
        WHERE 
            DATE(extraction_datetime) = '{date_input.isoformat()}'
        ;
    """, ttl="5m")
    st.dataframe(data=df)

# another way of using a date filter is applied it after, but including a where clause in the SQL query would be better
# especially for large datasets, otherwise the index created on the date column won't be useful
# filtered_df = df[df['Data'] == date_input]
# st.dataframe(data=filtered_df)
