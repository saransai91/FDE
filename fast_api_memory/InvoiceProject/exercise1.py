
import json

DATA_FILE = "data/invoices.json"

with open(DATA_FILE, "r") as f:
    invoices = json.load(f)

vendor_totals = {}

for invoice in invoices:
    vendor = invoice["vendor"]
    amount = invoice["amount"]

    if vendor in vendor_totals:
        vendor_totals[vendor] += amount
    else:
        vendor_totals[vendor] = amount

for vendor, total in vendor_totals.items():
    print(f"{vendor}: {total}")
