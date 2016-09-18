# Slack Timetable Bot

This is a Python bot that checks for new changes in the
timetable at [this](http://lyceum.urfu.ru/study/izmenHtml.php) page and sends the changes for 10E and 11E to Slack.

## How It Works?

The bot is hosted at Heroku and is being triggered every hour.
When new changes are present, it sends them to a Slack channel and records the change date to avoid sending the same notification over and over again.

## Requirements

**[Slacker](https://github.com/os/slacker)**

## Contributing

You can suggest new features and add your own using the pull requests' section. Heads on!

## TODO

- [x] Write a bot.
- [x] Add logging.
- [x] Rewrite message format to json and send text as attachment for better view.
- [x] _Epic_ :sparkles:: Add a web interface.
- [x] _The **most** epic_ :saxophone::turtle:: Add push notifications.

Stay tuned. :rocket:
