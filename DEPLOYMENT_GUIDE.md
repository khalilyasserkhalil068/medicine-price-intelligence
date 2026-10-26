# Deployment Guide — `Project Data Analysis` Project

> A practical guide for deploying the project's applications online or sharing them locally. All commands, file names, and technical terms are kept exactly as in the code, written in English inside `backticks`.

---

## 1) Short introduction

This project contains **two completely separate web applications**, and this is the most important thing to understand before any deployment:

| Application | Type | Entry point | Local server |
|---|---|---|---|
| **Streamlit** app | Multi-page application (`multipage`) | `app.py` + pages `pages/1_Overview.py` … `pages/6_Data_Explorer.py` | Port `8501` |
| **Flask** dashboard | Single-page dashboard serving `dashboard/templates/index.html` | `dashboard/app.py` | Port `5000` |

### The difference between local running (local) and hosting on a server (hosting)

- **Local running:** You run the application on your own machine. The application listens on `localhost` (i.e. `127.0.0.1`), meaning only you can open it from the same machine. The helper tools `run_streamlit.bat` and `run_dashboard.bat` do exactly this.
- **Hosting on a server (hosting):** You upload the code to a server running 24 hours a day, and that server serves the application and gives it a public link (`URL`) that anyone can open from anywhere in the world. However, no `.bat` files work there (there is no Windows), and the server defines the run command itself (`start command`).

### Which application to host where?

- The **Streamlit app** is the most suitable for deployment. Platforms like `Streamlit Community Cloud` and `Hugging Face Spaces` are designed from the start to run Streamlit apps with minimal effort, and this is the project's main application (6 analytics pages).
- The **Flask dashboard** must be hosted completely separately on a public `PaaS` service (such as `Render` or `Railway`) or on a private server/`Docker`, and it needs a production `WSGI` server (such as `Gunicorn` or `Waitress`) — and that is not something Streamlit platforms do.

> **Golden rule:** one platform = one application. Do not try to serve a Flask app on `Streamlit Community Cloud` or vice versa, because the two run in completely different ways.

---

## 2) Preparing the project before deployment

### 2.1 The `requirements.txt` file

The file already exists in the project root, and this is its content:

```text
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.20.0
plotly>=5.15.0
beautifulsoup4>=4.10.0
jupyter>=1.0.0
flask>=3.0.0
sqlalchemy>=2.0.0
pyodbc>=4.0.0
```

**An important point for you:** the **`flask`** package is **already listed** in `requirements.txt` (the line `flask>=3.0.0`), meaning the `dashboard/app.py` dashboard needs no package additions before its own deployment. ✅

**Useful notes (without modifying anything):**

- The code actually used at runtime: the Streamlit pages import `plotly`, `pandas`, and `numpy`, and the Flask app imports only `flask`. The other packages (`beautifulsoup4`, `jupyter`, `sqlalchemy`, `pyodbc`) most likely belong to the cleaning/analysis stage in `notebooks/`, not to web runtime. Heavy packages like `jupyter` and `pyodbc` lengthen the environment build time in the cloud — but **do not remove them** without confirming that no code imports them, because some platforms build the environment from the same file for all applications.
- `pyodbc` on Linux needs external system libraries (such as `unixODBC`) that are placed in the `packages.txt` file (one package per line). If a build error appears because of it, add `unixODBC` — or make sure it is not imported in the runtime path.
- It is better to pin specific versions (`pinning`) if hosting starts performing unexpected upgrades, but the important thing is that the file remains in the repository root (or alongside the entry file).

### 2.2 The `data/medicine.db` database and the supporting files

- Both applications read from a **`SQLite` database named `data/medicine.db`** (its size is approximately `3.9 MB`) and it is **read-only at runtime**.
- Some ready-made data is also in `CSV` files inside `reports/analysis/`.
- **The database and the `CSV` files must be present inside the repository** when you upload the project to any hosting, because servers copy your files from `Git`. A size of ~4 MB is very suitable for ordinary `Git` (no need for `Git LFS`).
- If the file is excluded/locked in `.gitignore`, you must remove it from the list and add it: `git add data/medicine.db` then `git commit`.
- **Important warning:** some platforms (such as `Render`) have temporary system files (`ephemeral filesystem`); any modification to files is lost on restart. This is **not a problem** for us because the database is read-only and we do not write to it at runtime.

### 2.3 The difference between the two deployments (a critical point)

- **`Streamlit Community Cloud` cannot run a Flask app.** And `HF Spaces` in Streamlit mode likewise. And `Render`/`Railway` do not run a Streamlit app directly without a custom run command.
- That means this part is **two separate deployments**: a deployment for the Streamlit app (sections 3, 4, and 5), and an independent deployment for the Flask app (section 6). Do not try to merge them.

### 2.4 A note about your local machine

Your machine runs `Python 3.13`, while the old `run_streamlit.bat` file calls `py -3.12` (a version that does not exist on your machine, and this is what was causing the failure). The quick local solution without modifying the file is to run this command manually from the project folder:

```bash
py -3.13 -m streamlit run app.py
```

And normalize the same command if you use `python` directly. (This file and the other project files **have not been and will not be modified** within this guide.)

---

## 3) Option one — `Streamlit Community Cloud` (free)

This is the easiest path for the Streamlit app, and it takes minutes.

### Steps

1. Upload the project to a `GitHub` repository (public or private). The platform reads your files from `Git`.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign up with a `GitHub` account.
3. Click **`Create app`** in the top left/right corner of the workspace (`workspace`).
4. When it asks you **"Do you already have an app?"** choose **`Yup, I have an app`**.
5. Fill in the application details:
   - **`Repository`**: the repository name.
   - **`Branch`**: the branch (for example `main`).
   - **`Main file path`** (entry point): enter `app.py`.
   - **`App URL`** (optional): a `subdomain` name you choose, so the link becomes `https://<your-name>.streamlit.app`.
6. **`Advanced settings`** (optional):
   - **`Python version`**: Streamlit Community Cloud supports the versions of `Python` that are security-supported and uses `3.12` as the default setting. Choose the version you worked with locally as much as possible.
   - **`Secrets`**: a field for `secrets.toml`. **You do not need it here**, because the project does not use any keys or passwords (no `API keys` and no `secrets`).
7. Click **`Deploy`** and wait a few minutes (it gets slower if there are many packages).

> **`secrets` are not required:** the application reads only local files, so there is no additional configuration.

### Free tier limitations

- **App hibernation (`App hibernation`):** any application with no visits for **12 hours** automatically goes to sleep to save resources. The first person to visit a sleeping app clicks the **`Yes, get this app back up!`** button (any visitor can wake it, not necessarily the developer). You can recognize sleeping apps from the workspace via the moon icon.
- **Limited and shared resources:** all accounts have the same resources. The limits (as of February 2024 and expected to change from time to time):
  - `CPU`: from `0.078 cores` to `2 cores`.
  - `Memory`: from `690MB` to `2.7GB`.
  - `Storage`: up to `50GB`.
  - If the app exceeds the limits, it may slow down or show **`🤯 This app has gone over its resource limits.`** or **`😦 Oh no.`**.
  - There are additional resources you can request for "charitable/educational" (`good-for-the-world`) cases.
- **Linux environment:** the platform is based on `Debian Linux`, and all paths must use `/` (forward-slash), not `\`. The way your code builds paths (`Path(__file__).resolve().parent`) is compatible with that. ✅
- **Certain settings override `config.toml`:** the platform enforces specific values on settings such as `enableXsrfProtection = true` and `runOnSave = true` and others, and keeps only one `config.toml` file in the branch root.
- **Sensitive codes such as keys have no place here** — keep using `Secrets` if you need them in the future.

> Note: prices and limits change — if you need a confirmed number, **"check the official page"**.

---

## 4) Option two — `Hugging Face Spaces` (free)

A very good platform for Streamlit apps, and it has a free tier (with basic resources). **Important (2026):** Hugging Face has deprecated using `Streamlit` as the default `SDK`, and now recommends choosing **`Docker SDK`** and then using the `Streamlit` template. (You can still choose `Streamlit SDK` but it is deprecated — rely on `Docker` if you want to stay consistent with their latest updates.)

### Method (a) — the traditional `Streamlit SDK`

1. Create an account on [huggingface.co](https://huggingface.co/) and verify your email.
2. Go to [huggingface.co/new-space](https://huggingface.co/new-space) and choose a name for the space (`Space`).
3. In the **`SDK`** field choose `Streamlit` (or `Docker` — see method b). In the case of `Streamlit SDK`, a `README.md` file will be generated containing a `YAML` block:
   ```yaml
   sdk: streamlit
   sdk_version: 1.25.0
   ```
   (You can modify `sdk_version`, but unsupported versions may cause problems.)
4. Upload the project files to the repository: `app.py`, the `pages/` folder, `utils/`, `data/medicine.db`, `reports/analysis/`, `.streamlit/config.toml`, and `requirements.txt`.
5. The space will install the packages automatically from `requirements.txt`.
6. **Important restrictions:** in `Streamlit SDK` mode only port `8501` is allowed (the default port), so `config.toml` must not change the port. Free domains may go into idle mode (`sleep`) after a period of non-use.

### Method (b) — `Docker SDK` (currently recommended)

1. Create a new `Space` and choose `SDK = Docker`. A `README.md` will be generated containing:
   ```yaml
   ---
   title: Medicine Analytics
   emoji: 💊
   sdk: docker
   app_port: 8501
   ---
   ```
2. The default port for `Docker` spaces is `7860`, and you can change it with `app_port`. Since Streamlit runs on `8501`, set `app_port: 8501` (or keep `7860` and serve Streamlit on `7860` with the command below).
3. Add a `Dockerfile` in the root (see the format in section 6.3) with the Streamlit run command:
   ```dockerfile
   ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```
4. Upload the rest of the project files, and set `app_port` to match the port Streamlit is running on.
5. **Files written to disk are lost when the space restarts** — but this is not a problem for us because `medicine.db` is read-only.

---

## 5) Option three — `Render` / `Railway` (general PaaS)

These platforms are general (`general PaaS`) and run any Python command, so you can run the **Streamlit app** on them with a custom run command.

### Running Streamlit on a general PaaS

Because Streamlit runs a web server, you must bind it to the platform's port (which is given to it by the environment variable `$PORT`) and to all network addresses:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

`Render` steps:
1. Create an account on [render.com](https://render.com/) and connect a `GitHub` repository.
2. Click **`New` → `Web Service`**.
3. Settings:
   - **`Language`**: `Python 3`.
   - **`Build Command`**: `pip install -r requirements.txt`.
   - **`Start Command`**: the command above.
   - **`Instance Type`**: `Free`.
4. Deploy and wait for the build.

### Free tier limitations (Render)

- **Spinning down on idle (`Spinning down on idle`):** the free web service **sleeps after 15 minutes** with no incoming request, and wakes up as soon as a new request arrives — and the wake-up takes about **one minute** (the visitor sees a loading page during that).
- **Usage hours:** each workspace gets **750 machine hours (Free instance hours)** per month. A sleeping service does not consume from this balance. If you exhaust the balance, the service is disabled for the rest of the month and resets with the new month.
- **Files are lost on redeploy/hibernation** (`ephemeral filesystem`) — again, not a problem for us (read-only database).
- **`Free Render Postgres`** (if you need a database in the future) expires after **30 days** from its creation.
- **Railway** is also a good `PaaS` platform: the same principle — `Build Command` and `Start Command`, and connecting the project to `GitHub`. However, its plans and hour limits/prices change quickly, so **"check the official page"** for the current settings.

> Note: the free tiers on `Render` and `Railway` may sleep or have limited hours — suitable for a demo, but not guaranteed if you need continuous round-the-clock operation without idle time.

---

## 6) Deploying the Flask Dashboard

The `dashboard/app.py` dashboard is an ordinary `Flask` application (`single-page` + several `API` routes). At real deployment time, you **must not** use `app.run()` because it is a **development server** that is insecure and not designed to handle requests, and `Flask` itself explicitly warns against it for production use.

### 6.1 A production `WSGI` server

**On Linux (recommended) — `Gunicorn`:**

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

- `-w 4`: the number of workers (`workers`).
- `-b 0.0.0.0:8000`: binding on all addresses and port `8000`.
- `app:app`: means inside the module `app` (i.e. the file `app.py`) take the application object named `app`.

> **Important:** you must run the command from inside the `dashboard/` folder (because `dashboard/app.py` is the one that contains `app = Flask(__name__)`). If you run it from the project root, use the correct module path, for example from inside `dashboard`:
> ```bash
> cd dashboard
> gunicorn -w 4 -b 0.0.0.0:8000 app:app
> ```
> (And do not modify any project file — this command is just a way of running.)

**On Windows (your machine) — `Waitress`** (the alternative to `Gunicorn`, which does not run on Windows):

```bash
waitress-serve --port=8000 app:app
```

The same logic: `app:app` means the file `app.py` ← the object `app`. And if you need `waitress` in the cloud or on another machine, add it to the packages (`pip install waitress`).

### 6.2 Why is `app.run()` forbidden in production?

- The development server in `Flask` handles one request at a time, and does not manage processes (`workers`) or automatic restarts, and performance and stability are weak under pressure.
- In `run_dashboard.py` it uses `app.run(host="0.0.0.0", port=5000, debug=False)` — this is **ideal for local running and demos**, but **not suitable for production**.
- Production servers (`Gunicorn` / `Waitress`) provide multiple processes, better monitoring, and higher tolerance for concurrent requests.

### 6.3 The `Dockerfile` format (for deploying Flask)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# We copy the whole project so that data/medicine.db and reports/analysis/ are available
COPY . .

EXPOSE 8000

# We run from inside the dashboard folder where app.py exists
WORKDIR /app/dashboard
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Notes on the file:
- We used `python:3.12-slim` as the base image (light). You can replace it with the `Python` version supported on your machine.
- `WORKDIR /app/dashboard` is necessary because `app = Flask(...)` is located in `dashboard/app.py`.
- If you will work on a local Windows machine with Docker, change the `CMD` to:
  ```dockerfile
  CMD ["waitress-serve", "--port=8000", "app:app"]
  ```
- If the `build` fails because of `pyodbc`, add the line `unixODBC` in the `packages.txt` file or exclude the unused packages.

### 6.4 Deploying Flask on Render

The same `Web Service` section:
- **`Build Command`**: `pip install -r requirements.txt`
- **`Start Command`**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app` (use the `$PORT` that the platform gives instead of a fixed number).
- Make sure that `app.py` and `requirements.txt` are in a clear path, and that the module path `app:app` is correct with respect to the `Working directory`.
- Review the free tier limitations in section 5 (15 minutes hibernation, 750 hours/month).

---

## 7) Sharing the application locally on the network (without hosting)

If you want your colleagues on the **same Wi-Fi / LAN network** to open the application without any hosting:

### Streamlit method

Run the application bound to all addresses (`0.0.0.0`) so it listens to any device on the network:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Note: your `.streamlit/config.toml` file already contains `port = 8501` and `headless = true`, so this will most likely suffice:

```bash
streamlit run app.py
```

### Flask method

Modify the run command manually (without modifying any file) to run `run_dashboard.py` (it already binds `0.0.0.0` on `5000`):

```bash
python run_dashboard.py
```

### How to find your machine's address (`LOCAL-IP`)

On Windows, run from `PowerShell`:

```powershell
ipconfig
```

And take the **`IPv4 Address`** value (it looks like `192.168.x.x` or `10.x.x.x`). Then share with your colleagues on the same network:

```text
http://<LOCAL-IP>:8501     # for the Streamlit app
http://<LOCAL-IP>:5000     # for the Flask dashboard
```

### Considerations

- All devices must be on the **same network**.
- **Windows Firewall (`Windows Firewall`)**: the first time you run it, Windows may ask about allowing the connection — allow the private network (`Private network`) or open the port.
- The server runs only as long as your machine is on and the terminal is running.

---

## 8) Security notes and important limitations

- **The database is read-only (`read-only`)**: `data/medicine.db` is read and not written to at runtime, so there is no risk of data loss from write operations. But be aware that any platform with temporary system files (`ephemeral`) erases any disk modification on redeploy — and this does not affect us.
- **No authentication (`no authentication`) by default**: the Streamlit application has no built-in login system (`login`); anyone who has the link can open the application. If you need to restrict it:
  - **Option 1 — a simple password gate:** add a simple check at the top of `app.py` (for example using `st.text_input`) that compares against the key, and stops rendering (`st.stop()`) if it is wrong, and store the key in `st.secrets`, not in the code. (This is a modification to `app.py` — do it yourself if you like, and it is not part of this guide.)
  - **Option 2 — a private application on Streamlit Community Cloud:** if it is deployed from a `private` repository, choose **`Only specific people can view this app`** and invite visitors by email (invitees log in with Google or a one-time link).
- **The Flask application likewise has no default authentication**; if you need login, use an extension such as `Flask-Login` or an `HTTP Basic Auth` gate via a middleware (`reverse proxy`), or integrate the verification with the `API` endpoints.
- **The data is public**: the dataset "Assorted Medicine Dataset of Bangladesh" is a **public dataset published on `Kaggle`**, so there is no personal information (`PII`), and sharing it is safe from a privacy standpoint.
- **Streamlit Community Cloud security settings**: the platform enforces `enableXsrfProtection = true` and `showErrorDetails = false`, and this protects you from some default risks.
- **Do not upload any secrets (`API keys` / `passwords`) inside the code or the `Git` repository**. Use the `Secrets` feature in the deployment platform.
- **The supported Python upgrade**: use a version that is security-supported (the platform may force an upgrade if your version goes out of support).

---

## 9) Comparison table between deployment options

| Option | Application type | Cost | Difficulty | Idle behavior (Sleep) | Suitable for a university project demo |
|---|---|---|---|---|---|
| **Streamlit Community Cloud** | Streamlit only | Free | Very easy | Sleeps after **12 hours** without visits; wakes up from any visitor | ⭐⭐⭐⭐⭐ The most suitable for a Streamlit app |
| **Hugging Face Spaces** | Streamlit (Docker/`SDK`) and Gradio | Free (basic tier) | Easy/medium | May enter idle mode after a period of non-use (check the official page) | ⭐⭐⭐⭐ Very good |
| **Render** (Free) | Any application (general `PaaS`) | Free (with limits) | Medium | Sleeps after **15 minutes** without requests; wakes in ~a minute; **750 hours/month** | ⭐⭐⭐ Good (needs attention to hibernation) |
| **Railway** | Any application (general `PaaS`) | Limited free tier (check the official page) | Medium | Depends on the current plan and quotas | ⭐⭐⭐ Good |
| **Docker + private server / VPS** | Any application | Paid (full control) | Highest | Does not sleep (you are in control) | ⭐⭐ Overkill for a demo |
| **Local sharing (LAN)** | Both | Completely free | Very easy | None (as long as your machine runs) | ⭐⭐⭐⭐ Practical quickly for a demo in the hall |

**A quick recommendation for the project:**
- For the **Streamlit** app: start with **`Streamlit Community Cloud`** (the easiest and most suitable), or **`Hugging Face Spaces`** as an alternative.
- For the **Flask** dashboard: **`Render`** with `Gunicorn` + `$PORT`.
- For a quick demo inside the college: **local sharing over the network** (section 7).

---

## 10) Sources (the official sources that were opened and verified)

- Streamlit Docs — Prep and deploy your app on Community Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
- Streamlit Docs — Deploy your app (`main file path`, `Python version`, `Advanced settings`): https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit Docs — App dependencies (`requirements.txt`, `packages.txt`): https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- Streamlit Docs — Share your app (public/private, private apps): https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- Streamlit Docs — App settings (URL, secrets): https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-settings
- Streamlit Docs — Manage your app (resource limits, `App hibernation` 12 hours): https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- Streamlit Docs — Status & limitations of Community Cloud (Debian 11, enforced settings): https://docs.streamlit.io/deploy/streamlit-community-cloud/status
- Streamlit Docs — Deploy Streamlit using Docker (the `Dockerfile` format): https://docs.streamlit.io/deploy/tutorials/docker
- Streamlit Docs — Deployment tutorials (list of platforms): https://docs.streamlit.io/deploy/tutorials
- Hugging Face — Streamlit Spaces (notice of `Streamlit SDK` deprecation, port `8501`): https://huggingface.co/docs/hub/spaces-sdks-streamlit
- Hugging Face — Docker Spaces (`app_port` = `7860`): https://huggingface.co/docs/hub/spaces-sdks-docker
- Render Docs — Free tier (15-minute hibernation, 750 hours, temporary file system): https://render.com/docs/free
- Render Docs — Deploy a Flask App (`gunicorn app:app`): https://render.com/docs/deploy-flask

> **Disclaimer:** prices, limits, and idle hours change constantly on all platforms. The numbers mentioned above are what was verified from the official documentation on the date this guide was prepared; and for any final decision **"check the official page"** of the platform before relying on it.
