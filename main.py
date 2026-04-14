from research_agent.app import run


if __name__ == "__main__":
    import json
    report_path = 'data/research_report_*.json'
    latest_report_path = report_path.replace('data/research_report_', 'data/latest.json')
    with open(report_path) as report_file:
        report_data = json.load(report_file)
    with open(latest_report_path, 'w') as latest_file:
        json.dump(report_data, latest_file, indent=4)
    
    # Always create latest.json directly after saving the report file
    import shutil
    latest_path = 'data/latest.json'
    shutil.copyfile(latest_report, latest_path)

    import json
    import glob
    import os

    # Locate the most recent report file
    report_files = glob.glob('data/research_report_*.json')
    latest_report = max(report_files, key=os.path.getctime)

    # Read the content of the latest report
    with open(latest_report, 'r') as f:
        report_data = json.load(f)

    # Save the content to latest.json
    with open('data/latest.json', 'w') as latest_file:
        json.dump(report_data, latest_file, indent=4)

    
    import shutil

    latest_path = 'data/latest.json'
    shutil.copyfile(latest_report, latest_path)

    run()
