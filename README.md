# theatre
Simple Server Project.

Note - this is not meant to, in its current state, be used in anything other than a local testing environment. This is an application being developed as a learning exercise.

## What is this?
This is part of a learning project whose goal is to explore how to write a server and, in so doing, learn about networking.

This project is not designed to be used in any sort of production environment. As a learning project, there's a lot about serving content that I don't know and, thus, I'm sure this server is riddled with security holes/weaknesses. Consequently, I take no responsibility for any issues that may arise and, indeed, this should be used as little more than code to learn (or not) from. That said, I do intend for this to work so, in this sense, it should do what it is designed to do - serve web content.

## Parts
1. theatre - the server itself.
2. theatre_stats - scripts that collects and reports back statistics about usage.
3. theatre_auth_gen - a tool to generate login credentials if you set up authentication.

## Testing
A simple test of theatre is to use cURL to send a GET request:

```curl --silent localhost:8888 > /dev/null```

## Linting
I'm currently focusing on linting the code and aiming for a score > 9 for each of the three scripts. Here are the current scores:

theatre: 9.00
theatre_stats: 9.20
theatre_auth_gen: 10.00

NOTE: As I work through linting the code, it's possible that parts of the code will break so don't be surprised if things go wrong.

## Licences

### THEATRE
Licenced under the MIT Licence. (c) 2015 Bryan Smith.
