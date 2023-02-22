# stingray-ip-list
Small Python scripts which gather data about IP ranges required for the Stingray products.<br>
The scripts are meant to be run on a regular basis in order to stay up to date with changes in AWS and/or Stingray architecture.<br>

## SB3
Lists specific to the Stingray Business music player (SB3).<br>
Generates 2 lists of IP ranges that can be imported into firewalls.

### Stingray Only
The SB3 must be allowed to reach these IPs via http in order to acquire the date and time.

### Stingray and AWS
The SB3 must be allowed to reach these IPs via https in order to download content, playlists, messages, and software updates.<br>
The player also requires these hosts to connect to Stingray servers for the purposes of monitoring, diagnostics, and to remotely control the player.

## Running manually
The script is intended for Python 3.9+ due to use of type hints from the standard collections.<br>
`requests` is used for downloading Amazon's data file. There are no other external dependencies.
