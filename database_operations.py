import json
from db_connection import get_db_connection

def insert_resume(response):
    """Insert parsed resume data into the database."""
    db_connection = get_db_connection()
    cursor = db_connection.cursor()

    insert_query = """
    INSERT INTO resumes (name, skills, experience, education)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_query, ( 
        response['name'], 
        ', '.join(response['skills']), 
        ', '.join(response['experience']), 
        ', '.join(response['education']) 
    )) 

    db_connection.commit()
    cursor.close()
    db_connection.close()
