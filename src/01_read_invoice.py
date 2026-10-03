import csv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
csv_path = base_dir / "data" / "homework_invoices.csv"

total_invoices = 0
greater_than_100000 = 0
invalid_amount = 0

with open(csv_path, "r", encoding="utf-8", newline="") as file:

    reader = csv.DictReader(file)

    for invoice in reader:

        total_invoices += 1

        vendor = invoice["vendor"]
        amount = invoice["amount"]
        status = invoice["status"]

        print("\nInvoice ID:", invoice["invoice_id"])
        print("Vendor:", vendor)
        print("Amount:", amount)
        print("Status:", status)

        try:
            # Check for missing amount
            if amount == "":
                raise ValueError("Missing amount")

            # Convert amount to number
            amount = float(amount)

            # Check amount > 100000
            if amount > 100000:
                print("Amount is greater than 100,000")
                greater_than_100000 += 1

        except ValueError:
            print("Invalid or missing amount")
            invalid_amount += 1


print("\n========== SUMMARY ==========")
print("Total invoices read:", total_invoices)
print("Invoices greater than 100,000:", greater_than_100000)
print("Invoices with missing/invalid amount:", invalid_amount)