This is a project in the course Database Technology at LTH, where the task was to design a relational database based on a description of a company's process and needs, write the SQL code to create that database and then create a REST API which accessed the database to implement a given set of endpoints. The API is written in Python and implements endpoints for things like placing orders, adding new recipes and registering deliveries of ingredients. It uses an SQLite database with tables and triggers, and communicates with it with operations that are transactional and secure against SQL injection. Included in the repository is an ER diagram describing the database and the SQL code to create it. To use the API, first set up the database with ```sqlite3 project.sqlite < create-schema.sql``` and then start the server with ```python app.py```.

Key features:
- REST API in Python allowing HTTP communication with JSON input/output.
- SQLite database using triggers and transactions to maintain consistency and enforce constraints.
- Carefully designed schema satisfying BCNF, with foreign keys and join tables to model relationships.
- Input validation, error handling and resistance against SQL injection.
