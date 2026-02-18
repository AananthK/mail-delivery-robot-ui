# bootstrop file: configure system path for streamlit deployment
# always run streamlit from main repo directory

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_SRC = REPO_ROOT / "backend" / "src"

sys.path.insert(0, str(REPO_ROOT)) 
sys.path.insert(0, str(BACKEND_SRC))