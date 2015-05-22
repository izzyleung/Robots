GRE Word lover
================
Expand your GRE vocabulary.  
Gather a GRE word, convert its content to image, and publish it to Weibo every 10 minutes.

#Setup
SAE pre-installed modules are not included in `requirement.txt`. Please install those modules with the corresponding version on SAE by executing the following command:

```
pip install django==1.4.0 lxml==2.3.4 MySQL-python==1.2.3
```

Then, install `requests` by executing

```
pip install -r requirement.txt
```

And create a database called `gre_word_lover` in MySQL, and run the command
```
./manage.py syncdb
```
to initiate the database.

Load the words into the database with:
```
./manage.py loaddata fixtures/words.json
```

__Please Note: the copyright of all the vocabulary materials belongs to Mr. Chen Qi, and Mr Zhou shulin.__

Don't forget to edit `credential_example.py` to fill in your credentials, and rename the file to `credential.py`.

Also, provide an unique `SECRET_KEY` in `settings.py` under `grewordlover` folder.

Finally, launch the server with the command
```
./manage.py runserver
```
and everything should be up and running properly.

#What are those extra files:
Since users are not allowed to save an image to the storage on SAE, I have to save the generated image as an IO stream, so that I have to modify the code in `weibo.py` and `sns.py` to let it work properly.
All the images are generated using the font called `microhei.ttc` in the root folder.
Without proper css and js provided, Django Admin page will be broken on SAE, so I have to include those static files in this repo.
