# phone-number-manager
A service to manage information related to Fuck You Telecom phone numbers selected by our customers.



## Local Setup

* create a file at private/password.txt - this will be the root password for the mysql database instance

* start up the containers with:

  `docker compose up -d`

* load the database schema with:

  `docker compose exec -it db bash -c 'mysql -u root --password="$(cat /run/secrets/db-password)" fut_public_be < /seed/init.sql'`



## Development tips

* To connect to the MySQL database via CLI:

  `docker compose exec -it db mysql -u root --password="$(cat private/password.txt)" fut_public_be`

* To watch server logs for all the containers, start up with `docker compose up` (without -d)



## Deployment

### Initial setup

* create a file at `private/password.txt` containing a random string - this will be the root password for the mysql database instance

* for reCAPTCHA setup, the secret key should be saved in a file at `private/recaptcha_secret_key.txt`
  get secret key here: [https://www.google.com/recaptcha/admin/site/706529890/settings](https://www.google.com/recaptcha/admin/site/706529890/settings)

* start up the containers with:

  `docker compose up -d`

* generate the SSL cert for the server with:

  `docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d whatever.fu-tele.com`

* shut down the dev containers: `docker compose down`

* now, follow the same setup steps as above (create password, etc.), but start up the containers with the `--profile prod` argument, like:

  `docker compose --profile prod up -d`

* load the database schema with the same command as above



### Maintenance - pulling the latest updates from the repository into your local dev setup

* stop the existing containers
  `docker compose down`
* pull updates
  `git pull`
* re-create the database schema
  see above
* re-start the containers
  `docker compose up -d`

* Renewing the SSL certs (must be done every 3 months)
  `docker compose run --rm certbot renew`
