import pandas as pd

"""
🔐 Step 4 – Authorization rules
For appropriate tickets, a pure rule engine (no LLM) uses:

the employee's role, department, and
the ticket category (intent)
to decide:

allowed → proceed
needs_approval → stop with status = needs_approval
blocked_by_auth → stop with status = blocked_by_auth


The rule engine takes:

intent = hardware_issue
role = junior_engineer
department = engineering
It looks up these values in auth_rules.csv and finds rule R1:

hardware_issue,*,*,allowed - All employees can raise hardware issues.
So it returns something like:

auth_status = "allowed"
reason = "Standard support users are allowed to raise VPN issues."
💡 If, instead, the ticket had been an access_request from a junior engineer, this step might have produced needs_approval or blocked_by_auth.


"""
def apply_authorization_rules(intent, role, department):

    # Load the authorization rules from CSV
    rules_df = pd.read_csv('data/auth_rules.csv')

    # Filter rules based on intent, role, and department
    applicable_rules = rules_df[
        (rules_df['intent'] == intent) |
        (rules_df['intent'] == '*')
    ]
    applicable_rules = applicable_rules[
        (applicable_rules['role'] == role) |
        (applicable_rules['role'] == '*')
    ]
    applicable_rules = applicable_rules[
        (applicable_rules['department'] == department) |
        (applicable_rules['department'] == '*')
    ]

    # Determine the most specific rule
    if not applicable_rules.empty:
        # Sort by specificity: exact matches first
        applicable_rules['specificity'] = (
            (applicable_rules['intent'] != '*').astype(int) +
            (applicable_rules['role'] != '*').astype(int) +
            (applicable_rules['department'] != '*').astype(int)
        )
        applicable_rules = applicable_rules.sort_values(by='specificity', ascending=False)

        # Get the top rule
        top_rule = applicable_rules.iloc[0]
        auth_status = top_rule['outcome']
        reason = top_rule['comment']
    else:
        auth_status = "blocked_by_auth"
        reason = "No applicable authorization rule found."

    return auth_status, reason