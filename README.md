This is the command used to start up the celery instance for queue management
`celery -A proj worker -l INFO`

This is how you start and stop the redis server in the background
`brew services start redis`
`brew services stop redis`

This is how you generate a migration
`alembic revision --autogenerate -m "migration message"`

this is how you apply the migration
`alembic upgrade head`

Alembic and seed scripts are both different - not generating seed scripts with alembic
how to run seed scripts:
`python -m db.seed`
run the latest alembic revision before running seed scripts
