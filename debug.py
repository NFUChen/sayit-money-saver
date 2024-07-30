

import os
import main

os.environ["SQL_URL"] = "postgresql://wichen-admin:wichenwichen-admin@localhost:5440/db"
app = main.main(False)
breakpoint()