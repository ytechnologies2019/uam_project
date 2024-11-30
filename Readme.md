# UAM_Project Database Setup

This repository provides SQL scripts to set up the `UAM_Project` database, which contains user management and submission approval systems.

## Prerequisites

Before running the SQL script, ensure you have the following:
- A MySQL/MariaDB server installed and running.
- Appropriate privileges to create databases and tables.

## Steps to Set Up the Database

Follow these steps to create and populate the database with the necessary tables and sample data.

### 1. Create the Database

The script first creates a database named `UAM_Project`. If the database already exists, it will not be created again.

```sql
CREATE DATABASE IF NOT EXISTS UAM_Project;
USE UAM_Project;
