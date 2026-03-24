## The Quant Mind Reader

Live stage demo that presents a quant-style prediction terminal on a public screen, while a hidden control panel feeds backstage inputs in real time.

### What it includes

- Public display page with terminal-style UI and reveal animation
- Hidden control panel for backstage input and reveal control
- FastAPI backend with WebSocket broadcast

### Quick start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

3. Open the pages:

- Public display: http://YOUR_IP:8000/
- Hidden control: http://YOUR_IP:8000/control

Replace `YOUR_IP` with your laptop's local IP (for example, `192.168.1.25`).

### Notes

- The control panel can save predictions before reveal.
- The reveal button shows the prediction log on the public screen.
- Use the clear button to reset state for a new run.
