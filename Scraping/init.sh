#!/bin/bash

#chmod +x init.sh
#./init.sh

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install-deps 
playwright install

echo "Setup complete. You can now run main.py."
