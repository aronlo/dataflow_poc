Dataflow

- ls -l spikey-data*

- export GOOGLE_APPLICATION_CREDENTIALS=~/spikey-dataflow.json

- https://cloud.google.com/dataflow/pipelines/dataflow-command-line-intf

- sudo apt-get update

- sudo pip install apache-beam[gcp]

- sudo pip install oauth2client==3.0.0

- sudo pip install httplib2==0.9.2


- gcloud init

- gcloud auth login

- gcloud components update beta

# Open Cloud Shell
- mkdir spikey_dataflow

- cd spikey_dataflow

- cp ~/spikey_winery_list.csv .


# Create a wineries.py file and paste in code here
- nano wineries.py
#Create an "output" directory under spikey_dataflow
- mkdir output 

- python spikey_wineries.csv 




#Start with code editor open and Cloud Shell below it

- gsutil config

- gsutil mb -p spikey-dtflw gs://spikey-df-store/

- gsutil cp spikey_winery_list.csv gs://spikey-df-store/data/


- python spikey_wineries_dataflow.py


- gcloud dataflow jobs list

- export JOBID=<X>

- gcloud beta dataflow logs list $JOBID

- gcloud beta dataflow metrics list $JOBID




- mkdir spikey_revenue

- cd spikey_revenue


- mvn archetype:generate \
      -DarchetypeGroupId=org.apache.beam \
      -DarchetypeArtifactId=beam-sdks-java-maven-archetypes-examples \
      -DarchetypeVersion=2.6.0 \
      -DgroupId=spikey.revenue \
      -DartifactId=spikey-product-revenue \
      -Dversion="0.1" \
      -Dpackage=org.apache.beam.examples \
      -DinteractiveMode=false

- cd spikey=product-revenue

- mvn compile exec:java \
      -Dexec.mainClass=org.apache.beam.examples.SpikeyProductRevenue 

 mvn -Pdataflow-runner compile exec:java \
  -Dexec.mainClass=org.apache.beam.examples.SpikeyProductRevenue \
  -Dexec.args="--project=spikey-dtflw \
  --stagingLocation=gs://spikey-df-store/staging/ \
  --output=gs://spikey-df-store/output/product_revenue/prod \
  --runner=DataflowRunner"


 

python spikey_top_selling_products.py \
        --input gs://spikey-df-store/data/spikey_sales_weekly.csv \
        --output gs://spikey-df-store/output/top_selling/top \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=1   


python spikey_top_selling_products.py \
        --input gs://spikey-df-store/data/spikey_sales_weekly.csv \
        --output gs://spikey-df-store/output/top_selling/top \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=10



python spikey_top_selling_products.py \
        --input gs://spikey-df-store/data/spikey_sales_weekly.csv \
        --output gs://spikey-df-store/output/top_selling/top \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=10





python spikey_top_selling_products_bigquery.py \
        --input gs://spikey-df-store/data/spikey_sales_weekly.csv \
        --output spikey-dtflw:sales.product_revenue \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=4   

# query 
SELECT product_name, product_revenue
FROM `spikey-dtflw.sales.product_revenue`
ORDER BY product_revenue DESC



- mkdir spikey_sales
- cd spikey_sales


python spikey_hourly_sales.py \
        --input gs://spikey-df-store/data/spikey_sales_weekly.txt \
        --output gs://spikey-df-store/output/hourly_sales/sales \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=4   


python spikey_top_bottom_selling_products.py \
        --input gs://spikey-df-store/data/spikey_sales_weekly.txt \
        --output gs://spikey-df-store/output/top_bottom/ \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=5


python spikey_top_sellers_offers.py \
        --input1 gs://spikey-df-store/data/spikey_sales_weekly.txt \
        --input2 gs://spikey-df-store/data/spikey_offers.txt \
        --output gs://spikey-df-store/output/top_sellers_offers/ \
        --runner DataflowRunner \
        --project spikey-dtflw \
        --temp_location gs://spikey-df-store/tmp/ \
        --num_workers=5


- Create a pubsub topic  "spikey-real-time-sales"

- Go to BigQuery
- Under the "sales" dataset
- Create a new table "product_sales"
- Fields 
  --"product_name" of type string
  --"units_sold" of type integer


- Create job from template: spikey-sales-tracker
- PubSub to BigQuery
- Topic: projects/spikey-dtflw/topics/spikey-real-time-sales
- Table: spikey-dtflw:sales.product_sales
- Temp location: gs://spikey-df-store/tmp


{"product_name":"Nivea Sensitive Shaving Cream", "units_sold":3} 

{"product_name":"Cutecumber Girl s A-line Dress","units_sold":1} 
        
{"product_name":"FAB FASHION Women Wedges","units_sold":4} 
        
{"product_name":"Nivea Sensitive Shaving Cream","units_sold":21} 
        
{"product_name":"Puma Sports Women s Top","units_sold":8} 
        
{"product_name":"GM Power mate 4 Strip Surge Protector","units_sold":5} 
        
{"product_name":"Phillips Trimmer Q765","units_sold":1}

{"product_name":"Puma Sports T-Shirt ","units_sold":5} 
        
{"product_name":"Gucci Flora Luxury Perfume","units_sold":1} 
        
{"product_name":"Nivea Sensitive Shaving Cream","units_sold":4} 
        
{"product_name":"GM Power mate 4 Strip Surge Protector","units_sold":7}  


[
  {
    "product_name": "Gucci Flora Luxury Perfume",
    "units_sold": 4
  },
  {
    "product_name":"GM Power mate 4 Strip Surge Protector",
    "units_sold":12
  }
]

