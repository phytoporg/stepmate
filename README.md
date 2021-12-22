# Stepmate
Stepmate is a companion web app for Stepmania. This is very much a small side project for me at the moment so I'm trying to keep the project goals modest and tight, but Stepmate is primarily aiming to:
1) Make searching for songs in a well-populated Stepmania setup a triviality from a phone or other device.
2) Allow folks to create and manage song playlists for a user profile attached to a given Stepmania box.

Stretch goals which may never happen: 
- Integrations with Stepmania for queuing up songs in a social setting and smarter profile management to track song stats and performance
- On-the-fly song downloads from centralized song and stepchart repositories

At the moment, Stepmate has only been tested on Ubuntu Linux, but I do want to support Windows and other Linux flavors when I'm happier with the state of the basic feature set.

# Running Stepmate

## The Server
The server stores song data provided by the client and serves it all through a simple front-end. It needs to be running before the client attempts to reach it:

```sh
$ pipenv shell
$ ./scripts/test_server.sh
```

## The Client
The client is meant to run on a Stepmania machine, though currently any machine with a Stepmania-compatible songs directory and file hierarchy will do fine. Running the client will shoot over all of the song information in a user-specified songs directory root to a machine on the local network hosting the server. For starters, you can just do something to the effect of:

```sh
$ pipenv shell
$ ./scripts/run_client.sh ~/.stepmania-5.1/Songs localhost 8000
```
