import logging
import argparse
import psycopg2
import psycopg2.extras

#set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

#connect to DB
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def put(name, snippet):
    """Store a snippet with an associated name."""
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute("insert into snippets values (%s, %s)", (name, snippet))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            cursor.execute("update snippets set message=%s where keyword=%s", (snippet, name))
    connection.commit()
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """ Retrieve the snippet with a given name"""
    logging.info("Retrieving snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        row = cursor.fetchone()
    logging.debug("Snippet retrieved successfully.")
    if not row:
        # No snippet was found with that name.
        return "404: Snippet Not Found"
    return row [0]
    
def search(query):
    """Search for snippets containing query.
    Returns a list of snippets.
    """
    logging.info("Retrieving list of snippets matching query {!r}.".format(query))
    command = "select keyword, message from snippets where message like %s"
    with connection, connection.cursor() as cursor:
        cursor.execute(command, ('%' + query + '%',)) #Go over this line
        rows = [row for row in cursor.fetchall()] #how does the fetchall function works
    return rows   

def catalog():
        """Get the list of existing keywords in database.
        Returns a list of keywords.
        """
        logging.info("Retrieving list of snippet keywords.")
        command = "select keyword from snippets"
        with connection, connection.cursor() as cursor:
            cursor.execute(command)
            keywords = [row[0] for row in cursor.fetchall()]
        return keywords

def main():
    """Main function"""
    logging.info("Constructor parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
    #Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve the snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
    # Subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="Store a snippet")
    search_parser.add_argument("query", help="A query to search for in snippets.")
    
    # Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Store a snippet")
    
    arguments = parser.parse_args()
    
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "search":
        rows = search(**arguments) #do I only use ** when passing arguments to the function?
        log_message = "Sucessfully retrieved snippets:\n"
        log_message += '\n'.join('{!r}: {!r}'.format(name, snippet[:10] + '...')
        for name, snippet in rows)
        logging.info(log_message)
        print ("Snippets matching search query:\n{}".format(rows)) #is there a difference {} vs {!r}
    
        
    elif command == "catalog":
        keywords = catalog()
        logging.info("Sucessfully retrieved keywords catalog:\n{}".format('\n'.join(keywords))) #Go over "Join"
        print("Retrieved keywords:\n{}".format('\n'.join(keywords)))
    
        
if __name__ == "__main__":
    main()
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    