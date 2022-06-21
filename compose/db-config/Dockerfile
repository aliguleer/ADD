FROM postgres:14.2
WORKDIR /sql

COPY sql/create.sql .
RUN cat create.sql > /docker-entrypoint-initdb.d/init.sql

WORKDIR /
RUN rm -rf sql 



