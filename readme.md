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

