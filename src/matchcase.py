invoice_amount = 50000

match invoice_amount:
    case amount if amount < 1000:
        invoice_approver = "Supervisor"
    case amount if amount <= 50000:
        invoice_approver = "Manager"
    case _:
        invoice_approver = "Manager and Director"

print("Invoice Amount:", invoice_amount)
print("Approver:", invoice_approver)