import logging
import os

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/simulation.log",
    filemode="w",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)
