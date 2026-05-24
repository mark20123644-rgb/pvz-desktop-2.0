import server
import sys
import os

if __name__ == "__main__":
    try:
        server.main()
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            os._exit(0)
        except:
            sys.exit(0)
else:
    server.main()
