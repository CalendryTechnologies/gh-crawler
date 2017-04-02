GoHartsville (by Calendry Technologies) Web Crawler
===================================================

This is a Python library designed to scrape websites (for now specifically in the Hartsville, SC area) and gather information about event details. It is currently highly developmental.

What it is now
--------------

Currently, it can scrape specific sites with specific, hard-coded patterns for limited data. There isn't much to it right now.

What it will be
---------------

This project is planned to evolve into a generalized web crawler which will gather data sites without any programatic hard-coding of patterns. This is a list of the specific future work to be done (a definitely non-inclusive list):
* Generalize the parser to read a pattern string and apply it to a specific url to gather specific data from that style page
 * Allow pattern string to pass information through xpath filters and through Python functions for converting data to the correct format
  * Patterns will be able to have multiple options which will be evaluated in order until one works
 * Allow following of links between pages to allow more specialized extraction (i.e. a calendar list provides links to the individual event pages which are more detailed)
 * Support multiprocessing for convenience on multicore systems (and possibly distributed computing)
* Pattern matching processor which takes several example events from a site then creates a pattern file from the overlap between those events.
 * If an event cannot be parsed with the current pattern, it will be passed to here to solve that instance and update the pattern.
 * Create function which converts formats based on definition. (Basically a generalized form of strptime and strftime) for all kinds of string manipulation)
* Integrate with the database to upload events (and possibly in the future generalized models) to in the correct form to be recognized

Usage
-----

This will definitely change through the development process so this is not stable enough yet to be determined. However, there are a few things which must be set up to use this library.
* If you plan to use a database, you must set up the database and user accounts which you hope to access
* The database information should be placed in a file called ".env" with the format "DATABASE_URL=postgres://user:password@host:port/database" rather than hard-coded in script

Libraries
---------

Although these may change as development changes, this is a list of all proposed libraries and their purposes in the project:
* requests - quick and simple http requesting
* lxml - html parser with html traversing and xpath extraction
* dateutil - fuzzy datetime pattern matching (may be replaced by generalized converter function because conversion will need to be language independent)
* sqlalchemy - database ORM for sql dialect independence
* psycopg2 - Postgres integration with sqlalchemy (may be removed in future implementations in the attempt ad sql dialect independence)
* dotenv - allows parsing of .env files so secret keys (like database information) can be kept locally
