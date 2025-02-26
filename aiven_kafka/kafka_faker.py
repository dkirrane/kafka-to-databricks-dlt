from kafka_common import *
import random
from faker import Faker

fake = Faker()

# Initialize a counter variable
counter = 0


# Function or loop where key is assigned
def get_next_key():
    global counter
    counter += 1
    key = str(counter)
    return key


def generate_user_created(schema_registry_client):
    schema = get_latest_schema(schema_registry_client, "UserCreated")
    record = {
        "user_id": fake.uuid4(),
        "username": fake.user_name(),
        "email": fake.email(),
        "created_at": int(fake.date_time_this_year().timestamp() * 1000),
    }
    return schema, record


def generate_user_login_attempt(schema_registry_client):
    schema = get_latest_schema(schema_registry_client, "UserLoginAttempt")
    record = {
        "user_id": fake.uuid4(),
        "ip_address": fake.ipv4(),
        "success": fake.boolean(),
        "attempt_time": int(fake.date_time_this_month().timestamp() * 1000),
    }
    return schema, record


def generate_order_placed(schema_registry_client):
    schema = get_latest_schema(schema_registry_client, "OrderPlaced")
    record = {
        "order_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "total_amount": round(random.uniform(10, 1000), 2),
        "order_date": int(fake.date_time_this_month().timestamp() * 1000),
    }
    return schema, record


def generate_payment_processed(schema_registry_client):
    schema = get_latest_schema(schema_registry_client, "PaymentProcessed")
    record = {
        "payment_id": fake.uuid4(),
        "order_id": fake.uuid4(),
        "amount": round(random.uniform(10, 1000), 2),
        "status": random.choice(["SUCCESS", "FAILED", "PENDING"]),
        "processed_at": int(fake.date_time_this_month().timestamp() * 1000),
    }
    return schema, record


def generate_shipment_status(schema_registry_client):
    schema = get_latest_schema(schema_registry_client, "ShipmentStatus")
    record = {
        "shipment_id": fake.uuid4(),
        "order_id": fake.uuid4(),
        "status": random.choice(["PROCESSING", "SHIPPED", "DELIVERED", "RETURNED"]),
        "updated_at": int(fake.date_time_this_month().timestamp() * 1000),
    }
    return schema, record


def generate_inventory_update(schema_registry_client):
    schema = get_latest_schema(schema_registry_client, "InventoryUpdate")
    record = {
        "product_id": fake.uuid4(),
        "quantity": random.randint(0, 1000),
        "warehouse_id": fake.uuid4(),
        "update_type": random.choice(["RESTOCK", "SALE", "ADJUSTMENT"]),
        "updated_at": int(fake.date_time_this_month().timestamp() * 1000),
    }
    return schema, record


# Example usage
if __name__ == "__main__":
    for func in [
        generate_user_created,
        generate_user_login_attempt,
        generate_order_placed,
        generate_payment_processed,
        generate_shipment_status,
        generate_inventory_update,
    ]:
        schema, record = func()
        print(f"Function: {func.__name__}")
        print(f"Schema: {schema}")
        print(f"Record: {record}")
        print()
