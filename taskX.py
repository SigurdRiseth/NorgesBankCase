import json
import requests

# Parse Packages file
def parse_packages_file(file_path):
    """
    Parses a Packages file and extracts package information.

    Args: 
        file_path (str): Path to the Packages file.

    Returns:
        list[dict]: A list of dictionaries where each dictionary represents a package
        with keys like 'Package', 'Version', etc.
    """
    packages = []
    with open(file_path, "r") as f:
        package = {}
        for line in f:
            line = line.strip()
            if line == "":
                if package:
                    packages.append(package)
                    package = {}
            else:
                key, _, value = line.partition(":")
                package[key.strip()] = value.strip()
        if package:
            packages.append(package)
    print(f"Parsed {len(packages)} packages.")
    return packages

# Query OSV API in batch
def query_osv_batch(packages):
    """
    Queries the OSV API for vulnerabilities of a batch of packages.

    Args:
        packages (list[dict]): A list of dictionaries representing packages, each containing 'Package' and 'Version'.

    Returns:
        dict: The JSON response from the OSV API for the batch query.
    """
    url = "https://api.osv.dev/v1/querybatch"
    queries = [
        {
            "version": package["Version"],
            "package": {"name": package["Package"], "ecosystem": "Debian"},
        }
        for package in packages
        if "Package" in package and "Version" in package
    ]
    payload = {"queries": queries}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Find vulnerable packages
def find_vulnerable_packages_batch(packages):
    """
    Identifies vulnerable packages by querrying the OSV API in batches.

    Args:
        packages (list[dict]): A list of dictionaries representing packages, each containing 'Package' and 'Version'.

    Returns:
        list[dict]: A list of dictionaries where each dictionary represents a vulnerable package and includes its name, version and vulnerablilites.
    """
    results = []
    batch_size = 200  # Adjust this based on performance
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
        print(f"{(i + batch_size) / len(packages) * 100:.2f}% done")  # Progress update
    return results

if __name__ == "__main__":
    """
    Main script to parse a Packages file, query for vulnerabilities, and save the reults to a JSON file.
    """
    packages = parse_packages_file("ressurser/oppgavex/Packages")
    vulnerable_packages = find_vulnerable_packages_batch(packages)
    with open("vulnerable_packages.json", "w") as f:
        json.dump(vulnerable_packages, f, indent=4)
    print(f"A total of {len(vulnerable_packages)} vulnerabilities were found and saved to vulnerable_packages.json")