import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def create_connection():
	conn = None
	try:
		conn = mysql.connector.connect(
			host=os.getenv("DB_HOST"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASSWORD"),
			database=os.getenv("DB_NAME"),
			port=os.getenv("DB_PORT")
		)
		if conn.is_connected():
			print("Connection to MySQL DB successful")
	except mysql.connector.Error as e:
		print(f"The error '{e}' occurred")

	return conn


def close_connection(conn):
	if conn:
		conn.close()
		print("Connection to MySQL DB closed")


def fetch_data(conn, query):
	cursor = conn.cursor()
	try:
		cursor.execute(query)
		rows = cursor.fetchall()
		return rows
	except mysql.connector.Error as e:
		print(f"The error '{e}' occurred")
