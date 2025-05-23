[![progress-banner](https://backend.codecrafters.io/progress/http-server/73ff661f-6115-473c-9e83-3bc1f3cd0eb0)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is a sample and simple HTTP Server written based off the following Code Crafters challenge by Eric Tsendjav.
["Build Your Own HTTP server" Challenge](https://app.codecrafters.io/courses/http-server/overview).

[HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) is the
protocol that powers the web. Through this challenge I have built a simple HTTP/1.1 server
that is capable of serving multiple clients, multi threaded and handles some encoding and decoding options. Everything can be run locally and tested through the terminal using sample CURL requests like so: 
```bash
curl --http1.1 -v http://localhost:4221/user-agent -H "User-Agent: pineapple/grape-banana" -H "Connection: close"