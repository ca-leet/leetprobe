import argparse
import asyncio
import aiohttp

COMMON_PORTS = [80, 443, 8000, 8080, 8081, 8443, 8843, 9443]

async def probe(session, sem, domain, port, results):
    protocols = ['http', 'https']
    for proto in protocols:
        url = f"{proto}://{domain}:{port}"
        try:
            async with sem, session.get(url, timeout=5, allow_redirects=True, ssl=False) as resp:
                results.append(url)
                break  # Stop after first successful response
        except:
            continue

async def run_probe(domains, ports, output_file):
    sem = asyncio.Semaphore(100)
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for domain in domains:
            for port in ports:
                tasks.append(probe(session, sem, domain.strip(), port, results))
        await asyncio.gather(*tasks)

    unique_results = sorted(set(results))

    if output_file:
        with open(output_file, 'w') as f:
            for url in unique_results:
                f.write(url + '\n')
    else:
        for url in unique_results:
            print(url)

def main():
    parser = argparse.ArgumentParser(description="Probe subdomains for HTTP/S services on common ports.")
    parser.add_argument('-i', '--input', required=True, help='Input file with subdomains (one per line)')
    parser.add_argument('-p', '--ports', nargs='*', type=int, default=COMMON_PORTS, help='Custom ports to scan')
    parser.add_argument('-o', '--output', help='Optional output file to write live URLs')
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]

    asyncio.run(run_probe(domains, args.ports, args.output))

if __name__ == '__main__':
    main()
