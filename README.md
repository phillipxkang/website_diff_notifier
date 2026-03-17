# website_diff_notifier

## How to start
1. Make sure your Google account has 2FA enabled at https://myaccount.google.com/security
2. On the same page, at the account search bar, search for "App Password"
3. Enter in a safe password you will remember
4. On your computer, set up the environment variables for:
    - EMAIL_USER (your email address)
    - EMAIL_PASS (the password you set up earlier)
    - NOTIFY_EMAIL (the email you want to notify. this can be the same as EMAIL_USER)
5. Run `docker-compose up` 

## TODO
- Cycle through all websites, not just one
- Separate out website parsing logic from task function
- Write tests around parsing and diffing logic

