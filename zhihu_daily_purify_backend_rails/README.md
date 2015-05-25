Zhihu Daily Purify Backend Rails
================
The backend of Zhihu Daily deployed on Heroku.

# Setup
First, make sure you are using Ruby version `2.2.2`, you can modify the ruby version in `Gemfile`, and run `bundle update` to use version other than `2.2.2`, they should work but it is not guaranteed.

Then, install all the dependencies with the command:
```
bundle install
```

Next, create a database in PostgreSQL with the name `zhihu_daily_purify_web_development` with the command:
```
CREATE DATABASE zhihu_daily_purify_web_development;
```

And, run the database migration with the command:
```
rake db:migrate
```

Finally, launch the server with:
```
rails s
```

You should see the welcome page at `0.0.0.0:3000`
