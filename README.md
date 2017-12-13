# Guess-My-Search
A game made for learning Flask and flask-socketIO

## Needed packages
You need Anaconda (python 3.x) and Flask-SocketIO. To install Flask-SocketIO type *pip install flask-socketIO* in the terminal.

## The concepts of the game
Each player submits a search-string and an autocomplete for the given search-string. Every other player also submits an autocomplete for all players' search-strings. Google's autocomplete is also submittet. At the end of the round, each player votes for what auto-complete that is correct. If your autocomplete gets voted for, you get a point. If you vote for googles autocomplete, you get a point.
