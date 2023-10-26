# song-typing-study
gather and post-process data to determine the role of song genre on typing speed.
a CSV is exported for use in statistics software. though this study was conducted on non-randomized retrospective data, future research will include randomizing and controlling variables to make for a valuable written online publication of the results.

## data sources
* monkeytype.com table html page download
* spotify logs, as sourced from spotify data export and custom logger

## requirements
* spotipy==2.23.0
* pandas

## credentials
write `cred.py` to the project directory according to the following template
```py
client_id=""
client_secret=""
```

## known issues
* song log does not have correct time zones starting when the logger is used
* file paths and more are set in `main.py`
