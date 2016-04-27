Robots
================
Various robots.

#What are they?
- `gre_word_lover`: Gather a GRE word, convert its content to image, and publish it to Weibo every 10 minutes.
- `quora_weibot`: Automatically checks the tweets of @Quora every 30 minutes, and reposts them to Weibo.
- `quora_weibot_backend`: Tweets fetching service running on Heroku that supports "Quora Weibot".
- `zhihu-daily-purify-azure`: Backend of Zhihu Daily Purify, written in Python with Flask. 

Detailed description can be found under each project folder.

#__Warning__
Sina App Engine now charge you for using MySQL with ridiculous amount of money.
Think twice before deploying your code to SAE.

Shame on you, Sina!

#How to deploy the code to SAE
Pack all the dependencies by executing

```
./bundle_local.py -r requirement.txt
```

Commit the code by svn, and, upload SQL file in the PHPMyAdmin page. (If it is not provided, you can dump it from MySQL)

#Why include Django Admin static files
SAE doesn't seem to provide those CSS and JS files for its users. Without those files, Django admin page will not be displayed properly. In order to show the original look of the admin page, I have to include those static file in each Django repo deployed on SAE.

#Problems with publishing Weibo status
Now that Sina has blocked the hacking way to publish Weibo with leaked credential from 3rd party clients with higher privileges like Weico, it will be almost impossible to write a robot for Weibo. The quota for normal applications when it is not certified is pathetic. If you want more quota, you must have the application sent to Sina to get it certified, but they will have countless reasons to reject yours.  
The code that publishs Weibo in this robot does not work anymore, but it used to work. :-(
