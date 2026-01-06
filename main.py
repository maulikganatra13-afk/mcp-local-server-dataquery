from fastmcp import FastMCP
import os
import aiosqlite
import logging

# ---------- Logging ----------
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "sql_query_server.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file)]
)

# ---------- DB Paths ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "sql_demo.db")
logging.info(f"Database path: {DB_PATH}")

mcp = FastMCP("SQLQueryServer")


# ---------- Init DB ----------
def init_db():
    import sqlite3
    try:
        with sqlite3.connect(DB_PATH) as c:
            c.execute("PRAGMA journal_mode=WAL")

            c.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    price REAL NOT NULL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    country TEXT NOT NULL
                )
            """)

            # verify write permissions
            c.execute("INSERT OR IGNORE INTO users(name, country) VALUES ('_test', 'NA')")
            c.execute("DELETE FROM users WHERE name = '_test'")

            logging.info("Database initialized successfully with write access")

    except Exception as e:
        logging.error(f"Database initialization error: {e}")
        raise


# Initialize at module load
init_db()


# ---------- TOOLS ----------

@mcp.tool()
async def list_tables():
    """List all tables in the database"""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [r[0] for r in await cur.fetchall()]
            return {"status": "success", "tables": tables}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def describe_table(table: str):
    """Return schema of a table (column names & types)"""

    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(f"PRAGMA table_info({table})")
            rows = await cur.fetchall()

            if not rows:
                return {"status": "error", "message": f"Table '{table}' not found"}

            columns = [
                {
                    "name": r[1],
                    "type": r[2],
                    "nullable": not r[3],
                    "default": r[4]
                }
                for r in rows
            ]

            return {
                "status": "success",
                "table": table,
                "columns": columns
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def run_query(query: str):
    """
    Run all types of queries no restrictions on any operation
    """

    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(query)
            
            # Check if this is a query that returns rows (SELECT)
            if cur.description is not None:
                # Query returns rows (SELECT)
                cols = [d[0] for d in cur.description]
                rows = await cur.fetchall()
                
                return {
                    "status": "success",
                    "row_count": len(rows),
                    "rows": [dict(zip(cols, r)) for r in rows]
                }
            else:
                # Query doesn't return rows (INSERT, UPDATE, DELETE, etc.)
                await c.commit()  # Important: commit the transaction
                
                return {
                    "status": "success",
                    "rows_affected": cur.rowcount,
                    "message": f"Query executed successfully. {cur.rowcount} row(s) affected."
                }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# @mcp.tool()
# async def run_query(query: str):
#     """
#     Run all types of queries no restrictions on any operation
#     """

#     q = query.strip().lower()

#     # forbidden = ["drop", "delete", "update", "insert", "alter", "truncate"]

#     # if any(x in q for x in forbidden):
#     #     return {
#     #         "status": "error",
#     #         "message": "Only SELECT queries are allowed for safety"
#     #     }

#     # if not q.startswith("select"):
#     #     return {
#     #         "status": "error",
#     #         "message": "Query must start with SELECT"
#     #     }

#     try:
#         async with aiosqlite.connect(DB_PATH) as c:
#             cur = await c.execute(query)

#             cols = [d[0] for d in cur.description]
#             rows = await cur.fetchall()

#             return {
#                 "status": "success",
#                 "row_count": len(rows),
#                 "rows": [dict(zip(cols, r)) for r in rows]
#             }

#     except Exception as e:
#         return {"status": "error", "message": str(e)}


# @mcp.tool()
# async def insert_sample_data():
#     """Insert demo rows for testing queries"""

#     try:
#         async with aiosqlite.connect(DB_PATH) as c:
#             await c.executemany(
#                 "INSERT INTO cars(make, model, price) VALUES (?,?,?)",
#                 [
#                     ("Toyota", "Corolla", 15000),
#                     ("Honda", "Civic", 18000),
#                     ("Tesla", "Model 3", 42000)
#                 ]
#             )

#             await c.executemany(
#                 "INSERT INTO users(name, country) VALUES (?,?)",
#                 [
#                     ("Maulik", "India"),
#                     ("John", "USA"),
#                     ("Akira", "Japan")
#                 ]
#             )

#             await c.commit()

#             return {"status": "success", "message": "Sample data inserted"}

#     except Exception as e:
#         return {"status": "error", "message": str(e)}


# ---------- START SERVER ----------
if __name__ == "__main__":
    mcp.run()
