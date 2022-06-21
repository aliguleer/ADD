#!/usr/bin/env python

from array import array
import click
import pandas as pd
import pika
import psycopg2
import dataclasses
import numpy as np
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from dataclasses import dataclass
from functools import partial


@dataclass
class DbConfig:
    host: str
    port: int
    dbname: str
    username: str
    password: str


@click.command()
@click.pass_context
@click.option(
    "--host-mb",
    type=str,
    default="localhost",
    help="Message Broker host.",
)
@click.option(
    "--host-db",
    type=str,
    default="localhost",
    help="DB host.",
)
@click.option(
    "--port-mb",
    type=click.IntRange(min=1024, max=65535),
    default=5672,
    help="Message Broker port.",
)
@click.option(
    "--port-db",
    type=click.IntRange(min=1024, max=65535),
    default=5432,
    help="DB port.",
)
@click.option(
    "-e",
    "--exchange",
    type=str,
    default="",
    help="Exchange name.",
)
@click.option(
    "-t",
    "--exchange-type",
    type=click.Choice(["direct", "fanout", "topic", "header"], case_sensitive=False),
    default="direct",
    help="Exchange type.",
)
@click.option(
    "-q",
    "--queue",
    type=str,
    default="",
    help="Queue name.",
)
@click.option(
    "-k",
    "--routing-key",
    type=str,
    default="",
    help="Routing key.",
)
def cli(
    ctx: click.Context,
    host_mb: str,
    port_mb: int,
    host_db: str,
    port_db: int,
    exchange: str,
    exchange_type: str,
    queue: str,
    routing_key: str,
) -> None:
    config = DbConfig(
        host=host_db,
        port=port_db,
        dbname="postgres",
        username="postgres",
        password="pass",
    )

    with pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host_mb,
            port=port_mb,
        )
    ) as connection, connection.channel() as channel:
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

        channel.queue_declare(queue=queue)

        channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

        channel.basic_consume(
            queue=queue, on_message_callback=partial(dbop, config)
        )

        channel.start_consuming()


def dbop(
    config: DbConfig,
    channel: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
) -> None:
    z=body.decode().split(",")
    y=np.array(z)
    
    print(y)
    dbInsert(config,y)
    
    channel.basic_ack(delivery_tag=method.delivery_tag)

def dbInsert(
   config:DbConfig,
    y:array
)-> None:

    with psycopg2.connect(
            host=config.host, port=config.port, dbname=config.dbname, user=config.username, password=config.password
        ) as connection, connection.cursor() as cursor:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO Crypto (date, open, high,low,close,volume_BTC,volume_USD) VALUES(%s, %s, %s, %s, %s, %s, %s)",(y[1], y[3], y[4],y[5],y[6],y[7],y[8])

            )
            cursor.close()


if __name__ == "__main__":
    cli()
