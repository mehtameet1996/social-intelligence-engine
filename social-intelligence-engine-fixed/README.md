# Social Intelligence Engine (Fixed)

## Run
1. Put your Reddit creds in an `.env` file in the root (optional):
```
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

2. Start:
```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

## Notes
- If Reddit creds are not provided, discovery returns an empty list (system still boots).
