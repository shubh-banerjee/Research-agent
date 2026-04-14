from research_agent.app import run


if __name__ == "__main__":
    import json
    report_path = 'data/research_report_*.json'
    latest_report_path = report_path.replace('data/research_report_', 'data/latest.json')
    with open(report_path) as report_file:
        report_data = json.load(report_file)
    with open(latest_report_path, 'w') as latest_file:
        json.dump(report_data, latest_file, indent=4)
    run()
