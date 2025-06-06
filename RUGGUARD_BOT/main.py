# main.py - Project RUGGUARD All-in-One Bot

import os
import time
import requests
import tweepy
from datetime import datetime, timezone
from dotenv import load_dotenv

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================

# Load variables from the .env file (or from Replit Secrets)
load_dotenv()

class Config:
    """Holds all configurations and API keys."""
    API_KEY = os.getenv("X_API_KEY")
    API_KEY_SECRET = os.getenv("X_API_KEY_SECRET")
    ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

    # Ensure all keys are present
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
        raise ValueError("Error: Ensure all API variables (X_API_KEY, etc.) are set in .env or Replit Secrets.")

    # Bot Configuration
    BOT_USERNAME = "projectruggaurd"
    TRIGGER_PHRASE = "riddle me this"
    TRUSTED_LIST_URL = "https://raw.githubusercontent.com/devsyrem/turst-list/main/list"
    MIN_TRUSTED_FOLLOWERS = 3

config = Config()


# ==============================================================================
# 2. TRUSTED LIST HANDLER
# ==============================================================================

# Simple cache to avoid repeatedly hitting the GitHub URL
_trusted_accounts_cache = None
_cache_timestamp = 0
CACHE_DURATION_SECONDS = 3600  # Cache for 1 hour

def get_trusted_accounts():
    """
    Fetches the list of trusted accounts from GitHub.
    Uses a cache for efficiency.
    """
    global _trusted_accounts_cache, _cache_timestamp

    current_time = time.time()
    if _trusted_accounts_cache and (current_time - _cache_timestamp < CACHE_DURATION_SECONDS):
        print("Using trusted list from cache.")
        return _trusted_accounts_cache

    print("Fetching new trusted list from GitHub...")
    try:
        response = requests.get(config.TRUSTED_LIST_URL)
        response.raise_for_status()  # Check for HTTP errors
        
        # Clean and format the list
        accounts = {line.strip().lower() for line in response.text.splitlines() if line.strip()}
        
        _trusted_accounts_cache = accounts
        _cache_timestamp = current_time
        print(f"Successfully fetched {len(accounts)} trusted accounts.")
        return accounts
    except requests.RequestException as e:
        print(f"Failed to fetch trusted list: {e}")
        # If fetching fails, return the old cache if it exists, or an empty set
        return _trusted_accounts_cache if _trusted_accounts_cache else set()


# ==============================================================================
# 3. ANALYSIS ENGINE
# ==============================================================================

def analyze_user_account(client: tweepy.Client, user_id: str) -> dict:
    """
    Analyzes an X user account and returns a report as a dictionary.
    """
    print(f"Starting analysis for user ID: {user_id}")
    report = {"error": None, "data": {}}
    
    try:
        # Get primary user data using expansions to be efficient
        response = client.get_user(
            id=user_id,
            user_fields=["created_at", "description", "public_metrics", "verified"]
        )
        user = response.data
        if not user:
            report["error"] = "User not found."
            return report

        # Extract basic metrics
        account_age = datetime.now(timezone.utc) - user.created_at
        follower_count = user.public_metrics.get('followers_count', 0)
        following_count = user.public_metrics.get('following_count', 0)
        follower_ratio = follower_count / following_count if following_count > 0 else float(follower_count)

        report["data"] = {
            "username": user.username,
            "name": user.name,
            "id": user.id,
            "account_age_days": account_age.days,
            "created_at": user.created_at.strftime('%b %Y'),
            "is_verified": user.verified,
            "bio": user.description,
            "followers": follower_count,
            "following": following_count,
            "follower_ratio": round(follower_ratio, 2),
            "tweet_count": user.public_metrics.get('tweet_count', 0),
        }

        # Trusted Follower Cross-Check Analysis
        print("Checking trusted followers...")
        trusted_accounts_on_list = get_trusted_accounts()
        
        if user.username.lower() in trusted_accounts_on_list:
            report['data']['is_on_trusted_list'] = True
            report['data']['vouched_by_count'] = len(trusted_accounts_on_list) # Max score
        else:
            report['data']['is_on_trusted_list'] = False
            # Note: This check is limited by the Free X API tier.
            # A full implementation requires 'Basic' tier access or higher.
            report['data']['vouched_by_count'] = 0 # Placeholder
            report['data']['vouched_by_list'] = [] # Placeholder
            report['data']['trusted_check_note'] = "Follower check requires 'Basic' tier X API access or higher."

    except tweepy.errors.TweepyException as e:
        print(f"Tweepy error during analysis: {e}")
        report["error"] = f"Failed to fetch user data from X. The account might be protected. (Error: {e})"
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        report["error"] = "An internal error occurred during the analysis process."
        
    return report


# ==============================================================================
# 4. REPLY GENERATOR
# ==============================================================================

def generate_reply(analysis_report: dict) -> str:
    """
    Creates a clean reply string from the analysis report.
    """
    if analysis_report.get("error"):
        return f"🤖 Analysis failed. {analysis_report['error']}"

    data = analysis_report["data"]
    username = data['username']
    
    # Simple Trust Score Logic
    score = 0
    reasons = []

    if data['account_age_days'] > 365:
        score += 25
        reasons.append("✅ Account age > 1 year")
    if data['followers'] > 1000:
        score += 15
    if data['follower_ratio'] > 2:
        score += 20
        reasons.append("✅ Follower/Following ratio > 2")
    if data['is_verified']:
        score += 25
        reasons.append("✅ Verified Account")
    if data['is_on_trusted_list']:
        score = 100 # Full score if on the main list
        reasons.append("🚀 RUGGUARD Trusted List Member!")
    elif data['vouched_by_count'] >= config.MIN_TRUSTED_FOLLOWERS:
        score += 50 # Large bonus
        reasons.append(f"🔥 Vouched by {data['vouched_by_count']} trusted accounts!")

    score = min(score, 100) # Cap score at 100

    # Determine trust level
    if score >= 85:
        trust_level = "Very High 🟢"
    elif score >= 65:
        trust_level = "High 🟡"
    elif score >= 40:
        trust_level = "Medium 🟠"
    else:
        trust_level = "Low 🔴"

    # Build the Reply Text
    reply_text = f"""
    🤖 Trustworthiness Analysis for @{username}
    -----------------------------------
    📊 Trust Level: {trust_level} ({score}/100)

    📝 Summary:
    - Account Age: {data['account_age_days']} days (Created {data['created_at']})
    - Followers: {data['followers']} | Following: {data['following']}
    - Bio: {'Present' if data['bio'] else 'Empty'}

    💡 Key Signals:
    {' | '.join(reasons) if reasons else 'No strong signals detected.'}
    
    {data.get('trusted_check_note', '')}
    -----------------------------------
    A bot by #ProjectRUGGUARD
    """
    # Clean up extra whitespace from the multiline string
    return "\n".join(line.strip() for line in reply_text.strip().split('\n'))


# ==============================================================================
# 5. BOT STREAM LISTENER
# ==============================================================================

class BotStreamListener(tweepy.StreamingClient):
    """
    A listener that monitors the tweet stream for the trigger phrase.
    """
    def __init__(self, bearer_token, client_v2):
        super().__init__(bearer_token)
        self.client_v2 = client_v2 # Client for performing actions (get_user, reply)
        print("Bot Listener is ready and listening...")

    def on_tweet(self, tweet: tweepy.Tweet):
        """Called every time a new tweet matches the filter rules."""
        print(f"Detected tweet from @{tweet.author_id}: {tweet.text}")

        is_reply = tweet.referenced_tweets and tweet.referenced_tweets[0].type == 'replied_to'
        contains_trigger = config.TRIGGER_PHRASE.lower() in tweet.text.lower()

        if is_reply and contains_trigger:
            print(">>> Trigger Detected! <<<")
            original_tweet_id = tweet.referenced_tweets[0].id
            try:
                original_tweet_response = self.client_v2.get_tweet(original_tweet_id, expansions=["author_id"])
                original_tweet = original_tweet_response.data
                
                if not original_tweet or not original_tweet.author_id:
                    print("Could not retrieve the author of the original tweet.")
                    return
                
                target_user_id = original_tweet.author_id
                
                # Start the analysis
                analysis_result = analyze_user_account(self.client_v2, target_user_id)

                # Generate and send the reply
                reply_text = generate_reply(analysis_result)
                
                print(f"Sending reply to tweet ID: {tweet.id}")
                self.client_v2.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet.id)
                print(">>> Reply successfully sent! <<<")

            except tweepy.errors.TweepyException as e:
                print(f"Error while processing reply: {e}")
            except Exception as e:
                print(f"An unexpected error occurred in on_tweet: {e}")

    def on_error(self, status_code):
        print(f"Stream error: {status_code}")
        return True # Don't kill the bot on a rate limit error

    def on_connection_error(self):
        print("Stream connection error.")


# ==============================================================================
# 6. MAIN EXECUTION BLOCK
# ==============================================================================

if __name__ == "__main__":
    print("Starting RUGGUARD Bot...")

    try:
        # Initialize API v2 Client (for actions like get_user and reply)
        client_v2 = tweepy.Client(
            bearer_token=config.BEARER_TOKEN,
            consumer_key=config.API_KEY,
            consumer_secret=config.API_KEY_SECRET,
            access_token=config.ACCESS_TOKEN,
            access_token_secret=config.ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        print("API v2 Client successfully initialized.")
        
        # Initialize Stream Listener
        stream_listener = BotStreamListener(bearer_token=config.BEARER_TOKEN, client_v2=client_v2)

        # Clear out old filter rules (best practice)
        rules = stream_listener.get_rules().data
        if rules:
            stream_listener.delete_rules([rule.id for rule in rules])
            print("Old filter rules have been deleted.")

        # Add new filter rule to monitor mentions of the bot
        rule_string = f"@{config.BOT_USERNAME} {config.TRIGGER_PHRASE}"
        stream_listener.add_rules(tweepy.StreamRule(rule_string))
        print(f"New filter rule added: '{rule_string}'")

        # Start listening to the stream
        stream_listener.filter(expansions=["author_id"], tweet_fields=["referenced_tweets"])

    except tweepy.errors.TweepyException as e:
        print(f"Tweepy authentication or connection error: {e}")
        print("Please ensure your API keys are correct and have the necessary permissions.")
    except Exception as e:
        print(f"A fatal error occurred in main: {e}")