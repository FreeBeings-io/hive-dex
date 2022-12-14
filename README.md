# Hive DEX API


<p align="center">
  <img src="./logo.png" />
</p>


<p align="center">Market data for the Hive blockchain's internal decentralized exchange.</p>

---

## Production Deployment

Have a HAF server [setup](https://gitlab.syncad.com/hive/haf), populating data from relevant operations.

PSQL filtering set to the following in `hived`'s `config.ini` will work:

```
# Defines operations' types to track. Can be specified multiple times.

psql-track-operations = limit_order_create_operation limit_order_cancel_operation limit_order_create2_operation fill_order_operation limit_order_cancelled_operation

# enable filtering accounts and operations

psql-enable-filter = 1
```

Build from the Dockerfile and run the container with the following variables passed:

```
DB_HOST=ip_address_of_haf_db_server
DB_NAME=your_haf_db_name
DB_USERNAME=username
DB_PASSWORD=password
SERVER_HOST=127.0.0.1
SERVER_PORT=8080
SERVER_WORKERS=1
SCHEMA=hive_dex
RESET=false
```

To reset the database, set the `RESET` variable to `true`.

**Example**

Create `.env` file with the above variables in the root folder of the repo and run:

```
docker build -t hive-dex .
docker run -d -p 8080:8080 --env-file .env hive-dex
```

To reset the database on startup, set the `RESET` variable to `true`.
