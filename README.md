# phone-number-manager
A service to manage information related to Fuck You Telecom phone numbers selected by our customers.

# Setup

* create a file at private/password.txt - this will be the root password for the mysql database instance

* start up the containers with:

  `docker compose up -d`

* load the database schema with:

  `docker compose exec -it db bash -c 'mysql -u root --password="$(cat /run/secrets/db-password)" fut_public_be < /seed/init.sql'`


# Development

* To connect to the MySQL database via CLI:

  `docker compose exec -it db mysql -u root --password="$(cat private/password.txt)" fut_public_be`

* To watch server logs for all the containers, start up with `docker compose up` (without -d)
