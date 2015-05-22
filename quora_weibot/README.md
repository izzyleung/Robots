Quora Weibot
================
Automatically checks the tweets of @Quora every 30 minutes, and reposts them to Weibo.

#Setup
Since `Flask` and `MySQLdb` are pre-installed on Sina App Engine, I did not include them in `requirement.txt`.  
Please install those modules with the corresponding version on SAE by executing the following command:

```
pip install Flask==0.7.2 MySQL-python==1.2.3
```

Then, install the remaining dependencies by executing

```
pip install -r requirement.txt
```

Then create a database called `quorafetch` in MySQL, and crete the table using the code in `table_create.sql`.

Finally, edit `credential_example.py` to fill in your credentials, and rename the file to `credential.py`.

And run the server with

```
python quora_show.py
```
