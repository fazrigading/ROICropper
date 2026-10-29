import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.dirname(__file__))

try:
    import spaces

    @spaces.GPU
    def _roicropper_gpu_warmup():
        return None
except ImportError:
    pass

from roicropper.web import demo, launch

if __name__ == "__main__":
    launch()
