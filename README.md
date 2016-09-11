# Slack Timetable Bot 

This is a simplest Python script which checks whether there are new changes in the 
timetable at [this](http://lyceum.urfu.ru/study/izmenHtml.php) page.

## How It Works?

The bot hosts at Heroku and being triggered every hour using cron planner. 
When new changes are present, it sends them to Slack channel and puts a date of those changes to a text file
called `changes.txt`.

## Requirements

It uses the latest [Slacker](https://github.com/os/slacker) framework and nothing all.

## Contributing

You can suggest new features and add your own using the pull requests' section. Heads on!

## TODO

- [x] Write a bot.
- [ ] Add a logging option.
- [ ] Rewrite message format to json and send text as attachment for better view.
- [ ] _Epic_ :sparkles:: Add a web interface.
- [ ] _The **most** epic_ :saxophone::turtle:: Add push notifications.

Stay tuned :rocket:.
