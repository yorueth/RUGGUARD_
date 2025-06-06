# Project RUGGUARD 
This is the official repository for the Project RUGGUARD X (Twitter) Bot, designed to provide on-demand trustworthiness analysis for user accounts on the Solana Network and beyond. When triggered, the bot analyzes the author of a tweet and posts a concise report, helping to foster a more transparent and reliable online environment.

This project was built using Python with the Tweepy library and is designed to be easily deployed on Replit.

# ✨ Key Features
On-Demand Analysis: Trigger the bot by replying to any tweet with @projectruggaurd riddle me this.
Targeted Reporting: The bot correctly analyzes the author of the original tweet, not the user who triggered the bot.
Comprehensive Metrics: Analysis includes account age, follower/following ratio, bio content, and verification status.
Trusted Network Vouching: Checks if the target account is vouched for by a predefined list of trusted community members.
Single-File Deployment: The entire application is contained in a single main.py file for ultimate ease of setup and deployment.

# 🏛️ Code Architecture & Structure
For simplicity and ease of deployment, the entire bot's logic is contained within a single main.py file. However, the code is organized into distinct logical sections, each handling a specific responsibility. This maintains clarity and a modular-like design within the single script.

The key logical sections within main.py are :
Configuration : This top section defines a Config class that loads all necessary settings and API keys from environment variables (.env file or Replit Secrets). This keeps all configurable parts in one place.

Trusted List Handler : A set of functions responsible for fetching the list of trusted accounts from the project's GitHub repository. It includes a simple caching mechanism to improve performance and avoid excessive requests.

Analysis Engine : A core function (analyze_user_account) that takes a user ID and performs the trustworthiness analysis. It fetches user data via the X API and calculates various metrics.

Reply Generator : The generate_reply function, which takes the raw analysis data and formats it into a clean, human-readable report to be posted as a reply on X.

Bot Stream Listener : The BotStreamListener class, which inherits from tweepy.StreamingClient. This is the heart of the bot, responsible for listening to the X stream for the trigger phrase and orchestrating the analysis/reply process.

Main Execution Block : The standard if __name__ == "__main__": block that initializes the X API client, sets up the stream listener rules, and starts the bot.

# ⚙️ Setup and Installation
Follow these steps to get the bot running on your local machine or on Replit.

1. Prerequisites
Python 3.8 or newer.
A free X Developer Account with an App attached to a Project to get your API keys and tokens.
2. Get the Code
Save the code from the single file provided into a new file named main.py.

3. Create the Dependencies File
In the same directory as main.py, create a file named requirements.txt and add the following lines:

Plaintext

tweepy==4.14.0
requests==2.31.0
python-dotenv==1.0.1
Then, install these dependencies by running:

Bash

pip install -r requirements.txt
4. API Key Configuration (Crucial)
The bot requires 5 keys from your X Developer Portal to function. Never share these keys or commit them to a public repository.

Local Machine Setup
Find your keys in the "Keys and Tokens" section of your app in the X Developer Portal. You'll need:

API Key
API Key Secret
Access Token
Access Token Secret
Bearer Token
In the project's root directory, create a new file named .env.

Copy the format below into your .env file and paste your keys.

Code snippet

# .env file for local configuration
X_API_KEY="YOUR_API_KEY_HERE"
X_API_KEY_SECRET="YOUR_API_KEY_SECRET_HERE"
X_ACCESS_TOKEN="YOUR_ACCESS_TOKEN_HERE"
X_ACCESS_TOKEN_SECRET="YOUR_ACCESS_TOKEN_SECRET_HERE"
X_BEARER_TOKEN="YOUR_BEARER_TOKEN_HERE"
Replit Setup
Replit provides a secure way to store these keys without using a .env file.

In your Replit project, go to the "Secrets" tab in the left sidebar.
Create a new secret for each of the 5 keys. The key name must match the variable name exactly, and the value will be your credential.
X_API_KEY = your_api_key
X_API_KEY_SECRET = your_api_key_secret
X_ACCESS_TOKEN = your_access_token
X_ACCESS_TOKEN_SECRET = your_access_token_secret
X_BEARER_TOKEN = your_bearer_token

# ▶️ How to Run the Bot
Once the setup and configuration are complete, running the bot is simple.

Open your terminal or the Replit shell.
Navigate to the directory containing main.py.
Run the script:
Bash

python main.py
If successful, you will see the following output in your console, and the bot is now actively listening for triggers on X :
Starting RUGGUARD Bot...
API v2 Client successfully initialized.
Old filter rules have been deleted.
New filter rule added: '@projectruggaurd riddle me this'
Bot Listener is ready and listening...

# ⚠️ Technical Note: Follower Checking Limitation
The project scope includes checking if a target user is followed by accounts from the trusted list. Please be aware that the Free tier of the X API does not provide a direct endpoint to efficiently check the followers of an arbitrary user. This functionality requires access to the 'Basic' tier or higher.

This bot's current implementation includes the necessary logic structure but will return 0 for the "vouched by" count due to this API limitation. This has been noted in the bot's reply to manage user expectations and demonstrate technical awareness.
