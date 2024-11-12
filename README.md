# octopus
It's a simple webscraping project to extract data from the octopus website.

Main libraries used:
- BeautifulSoup
- Selenium
- SqlAlchemy
- Streamlit

What it does:
 - Read the data about the plan offers in two different pages
 - Download the files for each offer when there is one with commercial cost below 100$
 - Load the extracted data in a PostgreSQL database
 - Visualize the data in a Streamlit app

## How to run and useful commands
- Create a venv and activate it. Python 3.12 was used in this project.
- To install the dependencies, run `pip install -r requirements.txt`
- Run the main webscraping script with `python main.py`
- You can run the unit tests by `python -m unittest`
- Start the streamlit app with `streamlit run app/dashboard.py` or `python -m streamlit run app/dashboard.py`

## Config Files
### Extraction
Create a yaml file named `local-config.yml` in the project folder (same level as `main.py`), eg: `octopus/local-config.yml`. The file must contain
```
base_url: "https://octopusenergy.it"
first_page: "/le-nostre-tariffe"

postgresql:
  host: insert_host_value_here
  user: insert_username_value_here
  pass: insert_password_value_here
  port: 5432
```

### Streamlit
Create a `secrets.toml` file in the `.streamlit` directory with this content:
```
[connections.postgresql]
type="sql"
dialect="postgresql"
username="insert_username_value_here"
password="insert_password_value_here"
host="insert_host_value_here"
port=5432
database="insert_database_value_here"
```


## DDL

### Create the main table
I could have used a normalized set of tables using another for the `user type` and another for the `rate type`, but it doesn't seem to be efficient 
considering the coding changes and complexity for a short string/varchar column value  
```
-- DROP TABLE public.plan_offer;

CREATE TABLE public.plan_offer (
	extraction_datetime timestamp NOT NULL,
	"name" varchar NOT NULL,
	raw_material_cost varchar NOT NULL,
	commercial_cost float4 NOT NULL,
	file_name_path varchar NOT NULL,
	time_rate_type varchar NOT NULL,
	user_type varchar NOT NULL
);
CREATE INDEX plan_offer_extraction_datetime_idx ON public.plan_offer USING btree (extraction_datetime);
```

### Data example
```
INSERT INTO public.plan_offer (extraction_datetime,"name",raw_material_cost,commercial_cost,file_name_path,time_rate_type,user_type) VALUES
	 ('2024-11-11 19:51:57.536419','Octopus Fissa 12M','0,1243 €/kWh',96.0,'E:/octopus/data/octopus_fissa_12m_2024-11-11.pdf','monoraria','domestiche'),
	 ('2024-11-11 19:51:57.536419','Octopus Flex','PUN + 0,011 €/kWh',96.0,'E:/octopus/data/octopus_flex_2024-11-11.pdf','multioraria','domestiche'),
	 ('2024-11-11 19:51:57.536419','Octopus Flex Mono','PUN + 0,011 €/kWh',96.0,'E:/octopus/data/octopus_flex_mono_2024-11-11.pdf','monoraria','domestiche');

```