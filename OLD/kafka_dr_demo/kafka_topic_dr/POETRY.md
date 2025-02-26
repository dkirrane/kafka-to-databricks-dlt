# Project Setup
```bash
# https://www.youtube.com/watch?v=R1uE4lVCs6I&t=900s
# https://docs.databricks.com/en/dev-tools/bundles/python-wheel.html#create-the-bundle-by-using-a-template
databricks bundle init

cd <bundle dir>
poetry init
poetry install
```

# Dependencies
```bash
poetry add pyspark
poetry add databricks-connect
poetry add databricks-dlt
poetry add confluent_kafka

poetry install
```

# Update lock
```bash
# If you change the Dependencies in pyproject.toml update the lock file
poetry lock
```

# VScode
poetry env info
poetry env info --path

You then want to bring up the command palette to select your Python Interpreter, and add one manually:


# Local dev
https://www.youtube.com/watch?v=AP5dGiCU188