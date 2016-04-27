Zhihu Daily Purify Backend - Azure
================
Backend of Zhihu Daily Purify, deployed on Azure (South Central US).  
Written in Python with Flask. Use MongoDB as persistence layer.

#Setup
Install the dependencies by executing
```
pip install -r requirement.txt
```

Rename the file `database.ini.example` to `database.ini`.  
Fill in your database configuration and credentials in the file.

Finally, launch the server with the command
```
python runserver.py
```
and everything should be up and running properly.

#Deploy to Azure
After setup, all you need to do is config the git remote url, and use the command `git push` to push the code to the server.
