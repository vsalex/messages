This small app is written by me for practice and demonstration purposes.
It can generate and read messages by different application instances.
All communication is via backend. Now supported only `redis`.

Requirements
============

* `Python >= 3.6`
* `Redis server` is necessary for now. It can be local or remote.

Installation
============
1. Clone this repo;
2. `pip install -r requirements.txt`;

Specification
=============
This app can generate and receive messages. All communication only via
configurable backend. All application copies but generator must be receivers.
Receivers are ready at any moment to receive message from backend.

All messages must be receive by single receiver. Generator must be single
instance. If generator shut downs - any of receivers must should be a
generator. All communication about who is generator only via backend do
not use OS features.

Messages are generated every 500 ms. To generate message use any function
with random text output.

Usage
=====
First of all you need to look at `settings.py` file and configure your
`MESSAGE_BACKEND_HOST` and `MESSAGE_BACKEND_PORT`. Don't forget to set
appropriate `LOG_LEVEL`.

And run a few instances via `python app.py`.

Have fun!
