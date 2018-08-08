Remedy API data pipeline
===================

This repo polls an inhouse api containing case files, and stores them in a postgres database. 

----------

Installation and usage
-------------
1. Pull the repo to a local directory
2. Install python 3.x into a local virtualenvironment, package requirements in `/requirements.txt`.

	```
	$ virtualenv .remedy_venv
	$ source .remedy_venv/bin/activate
	$ pip install requirements.txt 
	```
3. Create postgres database with the name 'remedy'

	```
	$ psql -u 'yourusername' -d postgres
	PSQL: CREATE DATABASE remedy;
	PSQL: \q
	```
	
4. Contact [@devonwalshe](https://www.github.com/devonwalshe) for the configuration payload, which by default looked for in a file at `./config/remedy_wsdl.xml`

5. The app exposes two clases, BoFetcher and BoCrawler
  - BoFetcher sends a single request, configured with a wsdl, and returns a parsed response
  - BoCrawler sets up a date range to traverse, DB connections, and traverses the date range filling in data
  - BoCrawler can crawl between two date ranges, or do a 'delta' search, which takes the date of the latest entry of in the DB as start, and time now as end. 
6. Typical flow in python console
  `from orm.models import *`
  `from BoCrawler import *`
  `crawler = BoCrawler('remedy_update', 'local', RemedyCase, delta=True)`
  `crawler.crawl()`





#### If you are missing archive records

1. Fetch all records from 'archive' api and store in your local DB
2. drop 'merge' psql table
3. 

Tunnel config
---
This is the local setup to allow you connect to the remote azure psql instance. There are two components:

1. An ssh tunnel that connects to an intermediary vitual machine on Azure that can connect to a managed PSQL instance
2. An SSL tunnel that sits in front of the SSH tunnel and encrypts the connection through the tunnel, allowing you to connect to the remote PSQL instance which requires SSL connections, without having to configure the client, which can be tricky. 

This is accomplished by setting up the ssh tunnel, installing and configuring stunnel, a service that sets up encrypted tunnels itself, and connecting to the remote database. You'll need passwords for the tunnel and the psql server. 

1. setup ssh tunnel to the remote server

	```
	  $ ssh -L 5555:devpgsql.postgres.database.azure.com:5432 gccdatauser@51.140.47.78 -N -vvv
	```

2. install stunnel
	
	On a mac:
	```
	$ brew install stunnel
	$ cd repo-directory && cp config/stunnel.conf /usr/local/etc/stunnel/stunnel.conf
	```
	On linux:
	```
	$ sudo apt-get install stunnel4
	$ cd repo_directory && cp config/stunnel.conf /etc/stunnel/stunnel.conf
	``` 
3. Connect to the psql instance

	```
	$ psql -h localhost -p 5556 -U gccadminuser@devpgsql -d gcc-dev-foi 
