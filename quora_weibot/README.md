Quora Weibot
================
Automatically checks the tweets of @Quora every 30 minutes, and reposts them to Weibo.

#Setup
Since `Flask` and `MySQLdb` are pre-installed on Sina App Engine, I did not include them in `requirement.txt`.  
Please install those modules with the corresponding version on SAE by executing the following command:

```
pip install Flask==0.7.2 MySQL-python==1.2.3
```

Then, install `requests` by executing

```
pip install -r requirement.txt
```

Then create a database called `quorafetch` in MySQL, and crete the table using the code in `table_create.sql`.

Finally, create a file called `credential.py` with the format:
```python
MYSQL_DB = 'YOUR_DATABASE_NAME_HERE'
MYSQL_USER = 'YOUR_USER_NAME_HERE'
MYSQL_PASS = 'YOUR_USER_PASS_HERE'
MYSQL_HOST_M = 'YOUR_HOST_M_HERE'
MYSQL_HOST_S = 'YOUR_HOST_S_HERE'
MYSQL_PORT = 'YOUR_MYSQL_PORT_HERE'

login_data = {
    'username': 'WEIBO_USER_NAME_HERE',
    'password': 'WEIBO_USER_PASS_HERE',
    'client_id': '2323547071', # This is the leaked credential of Weico
    'client_secret': '16ed80cc77fea11f7f7e96eca178ada3',
    'grant_type': 'password',
}

```

And run the server with

```
python quora_show.py
```

#Deploy to SAE
Pack all the dependencies by executing

```
./bundle_local.py -r requirement.txt
```

Then, commit the code by svn.

Upload `table_create.sql` in the PHPMyAdmin page.

#Problems with publishing Weibo status
Now that Sina has blocked the hacking way to publish Weibo with leaked credential from 3rd party clients with higher privileges like Weico, it will be almost impossible to write a robot for Weibo. The quota for normal applications when it is not certified is pathetic, but if you want more quota, and have the application sent to Sina to get it certified, they will have countless reasons to reject yours.  
The code that publishs Weibo in this robot does not work anymore, but it used to work. :-(
