"""
Employee Lookup Module

This module handles looking up employee profiles from users_roles.csv.
"""

import pandas as pd
from typing import Optional


def lookup_employee(employee_id: str) -> Optional[dict]:
    """
    Lookup employee profile based on employee_id.
    
    Args:
        employee_id: The ID of the employee to look up
        
    Returns:
        A dictionary containing the employee profile with keys:
        - employee_id
        - role
        - department
        - seniority
        
        Returns None if employee is not found.
    """
    # Load the users/roles data
    users_df = pd.read_csv('data/users_roles.csv')
    
    # Find the employee by ID
    employee_row = users_df[users_df['employee_id'] == employee_id]
    
    if employee_row.empty:
        return None
    
    # Convert to dictionary
    employee = employee_row.iloc[0].to_dict()
    
    return {
        "employee_id": employee.get("employee_id"),
        "role": employee.get("role"),
        "department": employee.get("department"),
        "seniority": employee.get("seniority")
    }
