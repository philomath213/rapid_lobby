# rapid_lobby
Rapid Lobby is a client/server app written in Python3 that allows multiple users to communicate over a shared channel.

# Installation

You need only Python3 to run the App.

```bash
$ git clone https://github.com/philomath213/rapid_lobby.git
```
# Usage
Running the server:

python rapid_lobby_cli.py create &lt;host&gt; &lt;port&gt; [-m MAX_CLIENTS_NUM]
```bash
$ python rapid_lobby_cli.py create 127.0.0.1 2130
[+] server started
```

Running the client:

python rapid_lobby_cli.py join &lt;host&gt; &lt;port&gt;
```bash
$ python rapid_lobby_cli.py join 127.0.0.1 2130
[+] Connected To: 127.0.0.1:2130
username: p213
[+] loggin ...
>> 
```
