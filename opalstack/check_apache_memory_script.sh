#!/bin/bash

# API endpoint and credentials
API_URL='https://my.opalstack.com/api/v1/account/info/'  # Replace with the actual API URL
API_KEY="21034553b13918172148e398395625194fbe6111"  # Replace with your actual API key
# Log file location
LOG_FILE="apache_memory_check.log"

# Function to log messages with datetime
log_message() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to restart Apache server
restart_apache() {
  log_message "Restarting Apache server..."
  cd ~/apps/server_apache/apache2/bin/
  ./apachectl restart
  log_message "Apache server restarted."

}

# Get server information from the API
response=$(curl -s -H "Authorization: Token $API_KEY" "$API_URL")

# Parse JSON response to extract RSS usage data
rss_total=$(echo "$response" | jq '.usage_data.webservers[].rss_total')
rss_used=$(echo "$response" | jq '.usage_data.webservers[].rss_used')

# Check if RSS used exceeds the limit
if [ "$rss_used" -gt 800 ]; then
  log_message "Memory usage exceeded. rss_used=$rss_used, rss_total=$rss_total"
  restart_apache
else
  if [ "$rss_used" -gt 500 ]; then
    log_message "Memory usage within limits. rss_used=$rss_used, rss_total=$rss_total"
  fi
fi
