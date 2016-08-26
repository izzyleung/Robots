Zhihu Daily Purify Backend
================
Backend of Zhihu Daily Purify, deployed on Heroku.  
Written in Python 3 with aiohttp. Use MongoDB as persistence layer.

# Setup
Install the dependencies by executing
```
pip3 install -r requirement.txt
```

Rename the file `database.ini.example` to `database.ini`.  
Fill in your database configuration and credentials in the file.

Finally, launch the server with the command
```
gunicorn ZhihuDailyPurify:app --worker-class aiohttp.worker.GunicornWebWorker --workers 4

```
and everything should be up and running properly.
