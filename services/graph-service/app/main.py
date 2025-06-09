import time
from correlation import run_correlation_job
from price_jump import run_price_jump_detection

if __name__ == "__main__":
    print("🚀 Graph Service (Python) Started")

    while True:
        try:
            run_correlation_job()
            run_price_jump_detection()
        except Exception as e:
            print(f"❌ Error occurred: {e}")
        
        time.sleep(60)  # runs every 60 seconds
