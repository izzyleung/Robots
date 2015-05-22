Zhihu Daily Purify Backend - Django
================
The backend of Zhihu Daily Purify deployed on SAE. (No longer working because the IP of SAE is blocked by Zhihu Daily's server)

#Setup
SAE pre-installed modules are not included in `requirement.txt`. Please install those modules with the corresponding version on SAE by executing the following command:

```
pip install django==1.4.0 MySQL-python==1.2.3
```

Then, install the remaining dependencies by executing

```
pip install -r requirement.txt
```

And create a database called `zhihudailypurify` in MySQL, and run the command
```
./manage.py syncdb
```
to initiate the database.

Don't forget to edit `credential_example.py` to fill in your credentials, and rename the file to `credential.py`.

Also, provide an unique `SECRET_KEY` in `settings.py` under `grewordlover` folder.

Finally, launch the server with the command
```
./manage.py runserver
```
and everything should be up and running properly.
