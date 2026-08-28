import sys, os
sys.path.insert(0, r"D:\VideoForgeSuite\server")
import orchestrator
print("HANDLER METHODS:")
for m in sorted(dir(orchestrator.Handler)):
    if not m.startswith("_") and not m.startswith("log"):
        print(" ", m)
print("MODULE LEVEL materials?:", hasattr(orchestrator, "materials"))