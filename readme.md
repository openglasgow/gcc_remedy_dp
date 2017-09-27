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
5. Single requests can be run from the command line, outputing JSON to sdout or piped to a file. Longer periods are broken down into batches, written to the DB and results logged. Date format for all the functions, in line with the api format, is Month-Day-Year or `%m-%d-%Y` in standard date parsing flags. Options are:
	* poll_remedy_api.py
		* -sd [start date]
		* -ed [end date]
		* -w [wsdl file location]
	* remedy_to_db.py
		* -sd [start date]
		* -ed [end date]
		* -b [batch size in days]
		* -s [sleep time between in seconds requests to manage server load]
	
	#### Examples
	``` 
	$ python poll_remedy_api.py -sd 01-01-2017 -ed 01-30-2017 -w config/remedy_wsdl.xml > remedy_jan_2017.json
	
	$ python remedy_to_db.py sd 01-01-2017 -ed 01-30-2017 -b 5 -s 5
	$ tail -f remedy_to_db.log
	``` 
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
