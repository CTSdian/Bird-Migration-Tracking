import traceback
from backend.data_loader import get_clustered_route_points
print("Calling backend.data_loader.get_clustered_route_points()...")
try:
    result = get_clustered_route_points()
    print("Success. Type:", type(result).__name__)
    print("Value preview:", repr(result)[:1000])
except Exception as e:
    print("EXCEPTION:", type(e).__name__, str(e))
    traceback.print_exc()
    raise
