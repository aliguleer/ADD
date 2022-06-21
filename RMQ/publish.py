#!/usr/bin/env python

from asyncore import read
from multiprocessing.connection import wait
from time import time
import click
import pika
import time


@click.command()
@click.pass_context
@click.option(
    "-h",
    "--host",
    type=str,
    default="localhost",
    help="Message Broker host.",
)
@click.option(
    "-p",
    "--port",
    type=click.IntRange(min=1024, max=65535),
    default=5672,
    help="Message Broker port.",
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
    "-k",
    "--routing-key",
    type=str,
    default="",
    help="Routing key.",
)
@click.option(
    "-i",
    "--input-path",
    type=click.Path(exists=True, dir_okay=False, allow_dash=True),
    default="-",
    show_default=True,
    help="Path to payload contents.",
)
def cli(
    ctx: click.Context,
    host: str,
    port: int,
    exchange: str,
    exchange_type: str,
    routing_key: str,
    input_path: str,
) -> None:
    with pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
        )
    ) as connection, connection.channel() as channel:
        with open(input_path, newline="") as f:
            lines = f.readlines()[1:]
            for row in lines:
                print(row)
                payload = row
                channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
                channel.basic_publish(
                    exchange=exchange, routing_key=routing_key, body=payload
                )
                time.sleep(3)


if __name__ == "__main__":
    cli()
