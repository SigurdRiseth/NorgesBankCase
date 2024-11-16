import json
import requests

# 1. Parse Packages file
def parse_packages_file(file_path):
    packages = []
    with open(file_path, "r") as f:  # Use `open` for plain text files
        package = {}
        for line in f:
            line = line.strip()
            if line == "":  # Blank line separates entries
                if package:
                    packages.append(package)
                    package = {}
            else:
                key, _, value = line.partition(":")
                package[key.strip()] = value.strip()
        if package:  # Add the last package entry
            packages.append(package)
    return packages

# 2. Query OSV API
def query_osv(package_name, version):
    url = "https://api.osv.dev/v1/query"
    payload = {"version": version, "package": {"ecosystem": "Debian", "name": package_name}}
    response = requests.post(url, json=payload)
    #print(f"Query: {payload}, Response: {response.status_code}")
    return response.json()

# 3. Find vulnerabilities
def find_vulnerable_packages(packages):
    results = []
    for package in packages:
        if "Package" in package and "Version" in package:
            vulns = query_osv(package["Package"], package["Version"])
            if vulns.get("vulnerabilities"):
                results.append({
                    "package": package["Package"],
                    "version": package["Version"],
                    "vulnerabilities": vulns["vulnerabilities"],
                })
    return results



# Query OSV API in batch
def query_osv_batch(packages):
    url = "https://api.osv.dev/v1/querybatch"
    queries = []
    
    # Construct batch queries
    for package in packages:
        if "Package" in package and "Version" in package:
            queries.append({
                "version": package["Version"],
                "package": {
                    "name": package["Package"],
                    "ecosystem": "Debian"
                }
            })
    
    payload = {"queries": queries}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Find vulnerable packages
def find_vulnerable_packages_batch(packages):
    results = []
    
    # Split packages into batches of 200
    batch_size = 200
    for i in range(0, len(packages), batch_size):
        batch = packages[i:i + batch_size]
        batch_results = query_osv_batch(batch)
        
        if batch_results and "results" in batch_results:
            for package, result in zip(batch, batch_results["results"]):
                if result.get("vulnerabilities"):
                    results.append({
                        "package": package["Package"],
                        "version": package["Version"],
                        "vulnerabilities": result["vulnerabilities"],
                    })
        else:
            print(f"Batch {i/batch_size} failed.")

        print(f"{i/len(packages)*100}% done")
    
    return results

# 4. Main script
if __name__ == "__main__":
    # Parse the packages file
    packages = parse_packages_file("ressurser/oppgavex/Packages")
    
    # Find vulnerable packages in the subset
    vulnerable_packages = find_vulnerable_packages_batch(packages)
    
    # Save the result to a file
    with open("vulnerable_packages.json", "w") as f:
        json.dump(vulnerable_packages, f, indent=4)
    
    print("Vulnerabilities for the first 10 entries saved to vulnerable_packages.json")