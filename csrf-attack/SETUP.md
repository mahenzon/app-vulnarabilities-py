# CSRF Demo Setup Instructions

## Prerequisites

- Docker and Docker Compose installed
- Python 3.x installed
- Certs issued for https (follow readme in `nginx-configs/certs` folder)

## Step 1: Configure Local Hosts

Add the following entries to your `/etc/hosts` file to map local domains:

### On macOS/Linux:

```bash
sudo nano /etc/hosts
```

Add these lines:
```
127.0.0.1 banking.test
127.0.0.1 attacker.test
```

Save and exit (Ctrl+O, Enter, Ctrl+X for nano).

### On Windows:

1. Open Notepad as Administrator
2. Open file: `C:\Windows\System32\drivers\etc\hosts`
3. Add these lines:
    ```
    127.0.0.1 banking.test
    127.0.0.1 attacker.test
    ```
4. Save the file

### Verify Configuration:

```bash
ping banking.test
ping attacker.test
```

Both should resolve to `127.0.0.1`.

## Step 2: Start Nginx in Docker

```bash
# Start nginx
docker-compose up -d
```

More helpful commands:

```shell
# Check logs (follow)
docker-compose logs -f

# Stop nginx
docker-compose down
```

## Step 3: Start the Banking Application

```bash
# go to app directory
cd fastapi-banking-app

# Initialize database
uv run db.py --reset

# Start the FastAPI server
uv run fastapi run --host 127.0.0.1 --port 8000 --proxy-headers
```

The banking app will be available at: https://banking.test (once nginx is running)


## Step 4: Access the Sites

- **Banking App**: https://banking.test
- **Attacker Site**: https://attacker.test

## Architecture

```
Browser Request
    ↓
    ├── https://banking.test → Nginx (Docker, host network)
    │                         ↓
    │                         Proxy to → FastAPI backend (localhost:8000)
    │
    └── https://attacker.test → Nginx (Docker, host network)
                               ↓
                               Serve static files from ./attacker-site/
```

## Troubleshooting

### nginx fails to start

Check if port 80 is already in use:

```bash
# macOS/Linux
sudo lsof -i :80

# Stop other services using port 80
sudo apachectl stop  # If Apache is running
```

### Banking app not accessible

1. Ensure the backend server is running on port 8000
2. Check nginx logs: `docker-compose logs nginx`
3. Verify `/etc/hosts` is configured correctly

### Attacker site not loading

1. Verify the `attacker-site` directory exists with `index.html`
2. Check nginx container logs: `docker-compose logs nginx`

## Notes

- The nginx configuration uses `host.docker.internal` to connect to services running on your host machine from within Docker
- On Linux, you may need to use `--add-host=host.docker.internal:host-gateway` if `host.docker.internal` doesn't work. The current config uses `network_mode: host` which avoids this issue
- With `network_mode: host`, nginx listens directly on your machine's port 80
