---
title: Simple Service Guide
menu: cdflow
weight: 6
---

# Simple Service Guide

This guide will help you quickly add some files in order for you to have a service ready to release and deploy with cdflow. We will show you the files you need to build a simple node.js service running in Docker.

You will need to have node.js, Docker. Create a folder and add the following files.

### package.json

To create a basic `package.json` in your project, run `npm init -Y`, this will accept the defaults when creating the `package.json` file.

### server.js

Create `server.js` in the root of the repository containing the following:

```javascript
require('http').createServer((req, res) => {
  res.writeHead(200, { 'Content-Type' : 'text/plain' })
  res.end('Hello, World!')
}).listen(8000)
```

### Dockerfile

Create `Dockerfile` in the root of the repository containing the following:

```dockerfile
FROM node:7-alpine
	
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
	
COPY package.json /usr/src/app/
RUN npm install
COPY . /usr/src/app
	
CMD [ "node", "server.js" ]
```

# Next

See how to use cdflow to deploy this simple service as a [frontend service](setting-up-a-frontend-service) or [backend service]().