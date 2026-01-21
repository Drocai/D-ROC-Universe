#!/usr/bin/env python3
"""
Check YouTube authentication status
"""
import os
import sys

print("AutoMagic YouTube Authentication Check")
print("=" * 50)

try:
    # Check if token exists
    if os.path.exists('token.pickle'):
        print("Found existing authentication token")
        print("Your system should already be authenticated!")
        print("")
        print("If uploads aren't working, the token might be expired.")
        print("Running YouTube upload will automatically refresh it.")
    else:
        print("No authentication token found")
        print("You'll need to authenticate when running YouTube upload")
    
    # Check credentials file
    creds_file = "client_secret_984577519807-gaplffli5mn8o57lb3cvkl9ldvo1rvlt.apps.googleusercontent.com.json"
    if os.path.exists(creds_file):
        print("YouTube credentials file: FOUND")
    else:
        print("YouTube credentials file: MISSING")
    
    print("")
    print("To find your email:")
    print("1. Visit: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
    print("2. See what Google account you're signed in with")
    print("3. Use that same email for YouTube upload authentication")
    print("")
    print("The system will automatically guide you through authentication!")
    
except Exception as e:
    print(f"Error checking authentication: {e}")

input("Press Enter to exit...")