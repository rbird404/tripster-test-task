# Test task from the company Tripster

## Local Development

### First Build Only
1. `cp .env.example .env`
2. `docker-compose up -d --build`

### Migrations
- Create an automatic migration from changes in `src/database.py`
```shell
docker compose exec app makemigrations *migration_name*
```
- Run migrations
```shell
docker compose exec app migrate
```
- Downgrade migrations
```shell
docker compose exec app downgrade -1  # or -2 or base or hash of the migration
```
