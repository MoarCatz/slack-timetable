# Slack Timetable Bot

This is a simple Python script that checks for new changes in the
timetable for 10E and 11E classes at [this](http://lyceum.urfu.ru/study/izmenHtml.php) page.

## How It Works?

The bot is hosted at Heroku and is being triggered every hour using `cron` planner.
When new changes are present, it sends them to Slack channel and puts a date of those changes to a text file
called `changes.txt`.

## Requirements

**[Slacker](https://github.com/os/slacker)**

## Contributing

You can suggest new features and add your own using the pull requests' section. Heads on!

## TODO

- [x] Write a bot.
- [x] Add logging.
- [x] Rewrite message format to json and send text as attachment for better view.
- [ ] _Epic_ :sparkles:: Add a web interface.
- [ ] _The **most** epic_ :saxophone::turtle:: Add push notifications.

Stay tuned :rocket:.
