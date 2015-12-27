<img src="http://www.bryanabsmith.com/ssp/ssp_windows.png"/>

# ssp
Simple web server for the "Summer Server Project."

Note - this is not meant to, in its current state, be used in anything other than a local testing environment. This is an application being developed as a learning exercise.

## What is this?
This is part of a learning project whose goal is to explore how to write a server and, in so doing, learn about networking.

This project is not designed to be used in any sort of production environment. As a learning project, there's a lot about serving content that I don't know and, thus, I'm sure this server is riddled with security holes/weaknesses. Consequently, I take no responsibility for any issues that may arise and, indeed, this should be used as little more than code to learn (or not) from. That said, I do intend for this to work so, in this sense, it should do what it is designed to do - serve web content.

## Testing
A simple test of spp is to use cURL to send a GET request:

```curl --silent localhost:8888 > /dev/null```


## Licences

### SSP
Licenced under the MIT Licence. (c) 2015 Bryan Smith.
