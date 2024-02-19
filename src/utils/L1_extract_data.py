from pg8000.native import identifier, literal  # Connection
from src.utils.get_most_recent_file import get_most_recent_file
from src.utils.flexible_formatter import format_data
from src.utils.get_timestamp import get_timestamp
from src.utils.write_csv import write_csv
# import boto3
# import json


def L1_extract_data(conn, s3, table_name, boolean, bucket_name):
    """
    This function takes a database connection, s3 client, table_name \n
    boolean value and bucket_name. Function extracts any new data from the database \n
    and writes to csv file within s3 bucket. 

    Args:

    `conn`: database connection
    `s3`: s3 client
    `table_name`: database table name
    `boolean`: output of 'is_bucket_empty' function
    `bucket_name`: s3 bucket name 

    ---------------------------
    Returns:

    No return value.


    """
    query_string = f'SELECT * FROM {identifier(table_name)}'
    if boolean is True:
        response = conn.run(f'{query_string};')
    else:
        latest_file = get_most_recent_file(s3, bucket_name, table_name)
        timestamp = get_timestamp(latest_file)
        query_string += f' WHERE last_updated > {literal(timestamp)};'
        response = conn.run(query_string)

    metadata = conn.columns
    column_names = [c['name'] for c in metadata]
    formatted_data = format_data(response, column_names)
    write_csv(table_name, bucket_name, s3, formatted_data)
