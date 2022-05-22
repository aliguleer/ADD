FROM postgres:14.2
WORKDIR /sql

COPY sql/create.sql .
COPY sql/insert.sql .
RUN cat create.sql insert.sql > /docker-entrypoint-initdb.d/init.sql

WORKDIR /
RUN rm -rf sql 



