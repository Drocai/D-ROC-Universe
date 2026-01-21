# OTTO Magic: Autonomous Content Engine

This is the production-ready code for OTTO Magic, a fully autonomous video creation and publishing system.

## Launch Instructions

1. **Install:** `pip install -r requirements.txt`
2. **Configure:** Copy `.env.example` to `.env` and fill in all required values.
3. **Authorize YouTube:** Run `python main.py authorize-youtube` once and follow the on-screen instructions to log in to your YouTube account. This creates the necessary token.
4. **Launch the Agent:**
    - In one terminal, run: `prefect server start`
    - In a second terminal, run: `prefect agent start -q default`
5. **Deploy the Workflow:**
    - In a third terminal, run: `python main.py deploy`

OTTO is now live and will run on the schedule defined in your `.env` file. To run it immediately for a test, use `python main.py run-now`.
