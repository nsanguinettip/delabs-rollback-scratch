#!/bin/sh
# Stand-in for an app that migrates at boot. QUERY is the read this version's code does; STRICT=1
# marks a version that checks the migration table even with RUN_MIGRATIONS=false (a stack that
# does not honor its skip variable); HEALTH_CODE is what it answers on every path.
set -e
until pg_isready -q -h db; do sleep 1; done
check() { for v in $(psql -tA -c "SELECT version FROM mig" 2>/dev/null); do [ -f "/migrations/$v.sql" ] || { echo "Can't locate revision $v"; exit 1; }; done; }
[ "${STRICT:-0}" = 1 ] && check
if [ "${RUN_MIGRATIONS:-true}" != "false" ]; then
  psql -q -v ON_ERROR_STOP=1 -c "CREATE TABLE IF NOT EXISTS mig (version text PRIMARY KEY)"
  check
  for f in /migrations/*.sql; do
    v=$(basename "$f" .sql)
    [ -n "$(psql -tA -c "SELECT 1 FROM mig WHERE version='$v'")" ] && continue
    psql -q -v ON_ERROR_STOP=1 -f "$f"
    psql -q -c "INSERT INTO mig VALUES ('$v')"
  done
fi
psql -q -v ON_ERROR_STOP=1 -c "$QUERY" >/dev/null
while true; do
  printf 'HTTP/1.1 %s X\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok' "${HEALTH_CODE:-200}" | nc -l -p 8080 >/dev/null 2>&1 || true
done
