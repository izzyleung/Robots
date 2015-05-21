SNS Robots
================
Various SNS robots.

#What are they?
- `quora_weibot_backend`: Tweets fetching service running on Heroku that supports "Quora Weibot".
- `quora_weibot`: Automatically checks the tweets of @Quora every 30 minutes, and reposts them to Weibo.

Detailed description can be found under project folder.

#Problems with publishing Weibo status
Now that Sina has blocked the hacking way to publish Weibo with leaked credential from 3rd party clients with higher privileges like Weico, it will be almost impossible to write a robot for Weibo. The quota for normal applications when it is not certified is pathetic. If you want more quota, you must have the application sent to Sina to get it certified, but they will have countless reasons to reject yours.  
The code that publishs Weibo in this robot does not work anymore, but it used to work. :-(
