
from collections import defaultdict
from copy import deepcopy

invoices = [
    {"invoice_id": "INV-101", "vendor": "ABC Ltd", "amount": 85000, "status": "PENDING", "date": "2026-09-03"},
    {"invoice_id": "INV-102", "vendor": "xyz corp", "amount": 142500, "status": "pending", "date": "2026-09-05"},
    {"invoice_id": "INV-101", "vendor": "ABC Ltd", "amount": 85000, "status": "PENDING", "date": "2026-09-03"},
    {"invoice_id": "INV-103", "vendor": "Globex", "amount": -550000, "status": "PENDING", "date": "2026-09-07"},
    {"invoice_id": "INV-104", "vendor": "ABC Ltd ", "amount": 62000, "status": "PAID", "date": "2026-09-08"},
    {"invoice_id": "INV-102", "vendor": "XYZ Corp", "amount": 150000, "status": "PENDING", "date": "2026-09-12"},
    {"invoice_id": "INV-105", "vendor": "Globex", "amount": 550000, "status": "PENDING", "date": "2026-09-09"},
    {"invoice_id": "INV-106", "vendor": "Initech", "amount": None, "status": "PENDING", "date": "2026-09-15"},
    {"invoice_id": "INV-107", "vendor": "ABC Ltd", "amount": 85000, "status": "PENDING", "date": "2026-09-03"},
]

payments = [
    {"invoice_id": "INV-101", "paid": 85000},
    {"invoice_id": "INV-101", "paid": 85000},
    {"invoice_id": "INV-104", "paid": 60000},
    {"invoice_id": "INV-109", "paid": 12000},
]

# 1. Normalize records in place using indexes.
invalid_amount_indexes = []

for i in range(len(invoices)):
    invoices[i]["vendor"] = invoices[i]["vendor"].strip().title()
    invoices[i]["status"] = invoices[i]["status"].upper()

    if invoices[i]["amount"] is None:
        invalid_amount_indexes.append(i)

print("1. Missing amounts:")
for i in invalid_amount_indexes:
    print(f"Index {i}: {invoices[i]}")

# Exclude missing-amount rows from further processing.
valid_invoices = [
    row for i, row in enumerate(invoices)
    if i not in invalid_amount_indexes
]

# 2. Find exact duplicates using all fields.
exact_dupes = defaultdict(list)
seen = {}

for i, row in enumerate(valid_invoices):
    # A sorted tuple makes a hashable key from every field.
    key = tuple(sorted(row.items()))

    if key in seen:
        if not exact_dupes[key]:
            exact_dupes[key].append(seen[key])
        exact_dupes[key].append(i)
    else:
        seen[key] = i

print("\n2. Exact duplicates:")
for key, indexes in exact_dupes.items():
    print(f"Indexes {indexes}: {dict(key)}")

# Keep the first record in each exact-duplicate group.
deduplicated = []
seen_keys = set()

for row in valid_invoices:
    key = tuple(sorted(row.items()))
    if key not in seen_keys:
        deduplicated.append(row)
        seen_keys.add(key)

# Preserve original indexes for later reporting.
deduplicated_with_indexes = []
seen_keys = set()

for original_index, row in enumerate(invoices):
    if original_index in invalid_amount_indexes:
        continue

    key = tuple(sorted(row.items()))
    if key not in seen_keys:
        deduplicated_with_indexes.append((original_index, row))
        seen_keys.add(key)

# 3. Suspected duplicates: same vendor, amount, date; different IDs.
print("\n3. Suspected duplicates:")

suspected_found = False

for i in range(len(deduplicated_with_indexes)):
    index_a, a = deduplicated_with_indexes[i]

    for j in range(i + 1, len(deduplicated_with_indexes)):
        index_b, b = deduplicated_with_indexes[j]

        if (
            a["vendor"] == b["vendor"]
            and a["amount"] == b["amount"]
            and a["date"] == b["date"]
            and a["invoice_id"] != b["invoice_id"]
        ):
            print(
                f"Index {index_a} and {index_b}: "
                f"({a['invoice_id']} ~ {b['invoice_id']})"
            )
            suspected_found = True

if not suspected_found:
    print("None")

# 4. Match negative invoices to positive partners.
# Same normalized vendor and same absolute amount.
print("\n4. Credit notes:")

credit_indexes = set()
positive_indexes = set()

for i, (idx_neg, negative) in enumerate(deduplicated_with_indexes):
    if negative["amount"] >= 0 or idx_neg in credit_indexes:
        continue

    partner = None

    for idx_pos, positive in deduplicated_with_indexes:
        if (
            positive["vendor"] == negative["vendor"]
            and positive["amount"] == abs(negative["amount"])
            and positive["amount"] > 0
            and idx_pos not in positive_indexes
        ):
            partner = (idx_pos, positive)
            break

    if partner:
        idx_pos, positive = partner
        negative["status"] = "CANCELLED"
        positive["status"] = "CANCELLED"
        credit_indexes.add(idx_neg)
        positive_indexes.add(idx_pos)
        print(f"{idx_neg} <-> {idx_pos}")
    else:
        print(f"Index {idx_neg}: No positive partner for {negative['invoice_id']}")

# 5. Reconcile payments by invoice ID.
print("\n5. Payment reconciliation:")

payment_totals = defaultdict(float)

for payment in payments:
    payment_totals[payment["invoice_id"]] += payment["paid"]

invoice_by_id = defaultdict(list)

for original_index, row in deduplicated_with_indexes:
    invoice_by_id[row["invoice_id"]].append((original_index, row))

for invoice_id, total_paid in payment_totals.items():
    matching = invoice_by_id.get(invoice_id, [])

    if not matching:
        print(f"{invoice_id}: ERROR - no matching invoice; paid={total_paid}")
        continue

    for idx, invoice in matching:
        amount = invoice["amount"]

        if invoice["status"] == "CANCELLED":
            print(f"{invoice_id}: ERROR - invoice cancelled")
        elif total_paid > amount:
            print(
                f"{invoice_id}: OVERPAID; "
                f"invoice={amount}, paid={total_paid}"
            )
        elif total_paid < amount:
            print(
                f"{invoice_id}: PARTIALLY PAID; "
                f"invoice={amount}, paid={total_paid}, "
                f"balance={amount - total_paid}"
            )
        else:
            print(f"{invoice_id}: FULLY PAID; amount={total_paid}")

# Vendor totals: exclude missing amounts and cancelled credit pairs.
print("\n6. Vendor totals:")

vendor_totals = defaultdict(float)

for _, row in deduplicated_with_indexes:
    if row["status"] != "CANCELLED":
        vendor_totals[row["vendor"]] += row["amount"]

for vendor, total in vendor_totals.items():
    print(f"{vendor}: {total}")
