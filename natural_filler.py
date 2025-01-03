import os
import random
import subprocess
from datetime import datetime, timedelta

# ================= CONFIGURATION =================
REPO_PATH = "./"
# Only touching .py files ensures valid python syntax for print() statements
TARGET_EXTENSIONS = [".py"] 
# =================================================

def get_file_list(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        if ".git" in root: continue
        if "natural_filler.py" in files: files.remove("natural_filler.py")
        for file in files:
            if any(file.endswith(ext) for ext in TARGET_EXTENSIONS):
                file_list.append(os.path.join(root, file))
    return file_list

def inject_code(filepath, original_content):
    """
    Takes the original content and inserts a random print statement 
    to simulate debugging.
    """
    lines = original_content.splitlines()
    
    # 1. Create a natural-looking print statement
    debug_msgs = [
        f'print("DEBUG: initialized service {random.randint(100,999)}")',
        f'print("[INFO] Connection established to port {random.randint(8000,9000)}")',
        f'print("Warning: Latency is high: {random.random():.2f}ms")',
        f'print("Checking integrity... {random.randint(1,100)}%")',
        f'print("Log: User session started.")',
        f'print("Debug: variable dump -> {random.randint(100,9999)}")'
    ]
    statement = random.choice(debug_msgs)
    
    # 2. Insert it safely (At the end is safest to avoid indentation errors)
    # If you want it at the top, we can put it after line 1 (imports)
    # But appending to end is 100% safe for all scripts.
    lines.append(f"\n{statement}")
    
    # Join it back
    return "\n".join(lines)

def git_commit(date_obj, message):
    date_str = date_obj.replace(
        hour=random.randint(9, 23), 
        minute=random.randint(0, 59), 
        second=random.randint(0, 59)
    ).isoformat()
    
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    
    subprocess.run(["git", "commit", "-m", message], env=env, check=False, stdout=subprocess.DEVNULL)

def get_valid_date(prompt):
    while True:
        try:
            date_str = input(prompt)
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid format! Please use YYYY-MM-DD")

def main():
    print("--- NATURAL GIT HISTORY FILLER (Print Statements) ---")
    
    # 1. INPUTS
    # start_date = get_valid_date("Enter Start Date (YYYY-MM-DD): ")
    # end_date = get_valid_date("Enter End Date   (YYYY-MM-DD): ")
    start_date = datetime.strptime("2025-01-03", "%Y-%m-%d")
    end_date = datetime.strptime("2025-03-09", "%Y-%m-%d")
    total_limit = int(input("Total commits desired (e.g. 15): "))

    # 2. CALCULATE DATES
    delta = end_date - start_date
    all_possible_days = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    if total_limit > len(all_possible_days):
        print(f"Warning: Not enough days. Capping at {len(all_possible_days)}.")
        selected_dates = all_possible_days
    else:
        selected_dates = sorted(random.sample(all_possible_days, total_limit))

    # 3. BACKUP ORIGINAL CONTENT
    print("\nReading original code...")
    files = get_file_list(REPO_PATH)
    if not files:
        print("Error: No .py files found." + str(dir()))
        return

    original_contents = {}
    for f in files:
        with open(f, "r", encoding="utf-8") as r:
            original_contents[f] = r.read()

    # 4. EXECUTE
    print(f"Generating {len(selected_dates)} commits...")
    
    for commit_date in selected_dates:
        # Pick a random file to "debug"
        target_file = random.choice(list(original_contents.keys()))
        
        # Inject a FRESH print statement into the ORIGINAL content
        # (This ensures we don't just keep adding lines forever, we replace the previous 'debug')
        modified_content = inject_code(target_file, original_contents[target_file])
        
        # Write it
        with open(target_file, "w", encoding="utf-8") as w:
            w.write(modified_content)
        
        # Commit it
        subprocess.run(["git", "add", target_file], check=False, stdout=subprocess.DEVNULL)
        
        msgs = ["added debug logs", "checking var values", "temp fix for logging", "debugging issue", "print debug info"]
        git_commit(commit_date, random.choice(msgs))
        
        print(f" -> {commit_date.date()}: Debugging '{os.path.basename(target_file)}'")

    # 5. FINAL RESTORATION
    print("\nRestoring original clean code...")
    for f, content in original_contents.items():
        with open(f, "w", encoding="utf-8") as w:
            w.write(content)
            
    subprocess.run(["git", "add", "."], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "Removed debug logs (Cleanup)"], check=False, stdout=subprocess.DEVNULL)
    
    print("\nDone! Your code is clean again.")
    print("Run: git push -f origin main")

if __name__ == "__main__":
    main()