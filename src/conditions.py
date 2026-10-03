invoice_amount = 50000

if invoice_amount < 1000:
    invoice_approver = "Supervisor"
elif invoice_amount <= 50000:
    invoice_approver = "Manager"
else:
    invoice_approver = "Manager and Director"

print("Invoice Amount:", invoice_amount)
print("Approver:", invoice_approver)