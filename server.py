
# Import main function
from src.server.main import server_main
from src.print import warning

# Run the main function
if __name__ == "__main__":
	warning("This server application is not secure, please use it only in a trusted environment")
	server_main()

