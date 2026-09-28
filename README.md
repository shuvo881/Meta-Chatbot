# Meta-Chatbot

A FastAPI app with Facebook/Meta OAuth login support.

## Features

- Build a Facebook login URL
- Handle the OAuth callback
- Exchange the authorization code for an access token
- Fetch the authenticated user profile from Meta Graph API

## Setup

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
2. Fill in your real Meta App values:
   - `FACEBOOK_APP_ID`
   - `FACEBOOK_APP_SECRET`
   - `FACEBOOK_REDIRECT_URI`
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```

## Auth flow

- Visit `http://localhost:8000/auth/facebook/login-url` to get the login URL.
- Redirect the user to that URL.
- Meta will redirect back to `FACEBOOK_REDIRECT_URI` with a `code` query parameter.
- The callback route exchanges that code for a token and fetches the user profile.

Example callback URL:
```text
http://localhost:8000/auth/facebook/callback?code=YOUR_CODE
```

## Important notes

- Facebook rejects invalid scopes such as `email` unless your app is configured and approved for that permission.
- The safe default is `FACEBOOK_LOGIN_SCOPE=public_profile`.
- If you need `email`, set `FACEBOOK_LOGIN_SCOPE=public_profile,email` only after the permission is approved in the Meta App dashboard.
- You must configure the same redirect URI in your Meta App dashboard.
- Use a valid existing app ID and app secret from Meta for Developers.
- In production, store secrets in environment variables or a secret manager.
