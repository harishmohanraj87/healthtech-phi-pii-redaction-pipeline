# 🗄️ Redis Integration & Mapping

This directory handles the temporary, secure storage of the relationships between the original sensitive data and their generated placeholder tokens.

## 🎯 Purpose
To safely store and manage "Forward Mapping" (Original Data -> Token) and "Reverse Mapping" (Token -> Original Data). This is the Re-identification engine that allows authorized users to retrieve the original clinical notes if needed.

## 📂 Files
* `mapping.py`: Contains the logic to connect to the Redis database, save the token-to-data mappings with an expiration time (TTL), and retrieve data using a token.
* `__init__.py`: Initializes the folder as a Python module.

## 🚀 Responsibilities (Member 3)
* Establish and maintain the Redis connection.
* Implement Placeholder Mapping (saving data).
* Implement the Re-identification engine (reverse mapping).
* Handle session persistence and optimize Redis performance.