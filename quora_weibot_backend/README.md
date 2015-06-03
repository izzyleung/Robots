Quora Tweets Fetch Backend
================
Tweets fetching service running on Heroku that supports "Quora Weibot".

#Why
I have most of the Robots hosted on Sina App Engine back then, because SAE provides both reliable, reasonably-priced service; an acceptable accessing speed for people living in mainland China; and a relatively fast speed to access Weibo service.  
While Twitter is censored in China, I have to use Heroku as a Springboard to break away from the censorship.

Some might argue that I can use Heroku service for both fetching tweets and publishing Weibo status.  
However, by using Heroku Scheduler to publish Weibo status periodically, I have to provide credit card info. I did not have my own credit card at that time, which rules out the possibility of this means.  
Moreover, Twitter's short URL service is not reachable in China, so I have to expand `t.co` links to the original ones, so that Weibo users are able to access the content @Quora shares on Twitter. (Though some links are still shadowed by GFW)

#Setup
- Install dependencies: `bundle instal`
- Edit `credential_example.rb` to fill in your Twitter credentials, and rename the file to `credential.rb`.
- Run the server: `bundle exec rackup -p 5000 config.ru`
- Done!

#Why store one day's news in a single entry?
Because the free version of PostgreSQL on Heroku only supports 10000 entries in a single database, I do not want to pay extra money for this accelerate server, so I have to save every day's news in a single entry. In the Django backend, I have to keep sync with the data so that I have to do the same thing.
