from enum import Enum


class TransactionType(str, Enum):
    Income = "Income"
    Expense = "Expense"


class IncomeCategory(str, Enum):
    Salary = "Salary"
    Bonus = "Bonus"
    Donation = "Donation"
    Sale = "Sale"
    Rent = "Rent"
    Refund = "Refund"
    Coupon = "Coupon"
    Lottery = "Lottery"
    Dividend = "Dividend"
    Investment = "Investment"
    Other = "Other"


class ExpenseCategory(str, Enum):
    Dining = "Dining"
    Utilities = "Utilities"
    Transportation = "Transportation"
    Home = "Home"
    Car = "Car"
    Entertainment = "Entertainment"
    Shopping = "Shopping"
    Clothing = "Clothing"
    Insurance = "Insurance"
    Tax = "Tax"
    PhoneBill = "PhoneBill"
    Smoking = "Smoking"
    Health = "Health"
    Fitness = "Fitness"
    Children = "Children"
    Pets = "Pets"
    Beauty = "Beauty"
    Electronics = "Electronics"
    Food = "Food"
    Alcohol = "Alcohol"
    Vegetables = "Vegetables"
    Snacks = "Snacks"
    Gifts = "Gifts"
    Social = "Social"
    Travel = "Travel"
    Education = "Education"
    Fruits = "Fruits"
    Books = "Books"
    OfficeSupplies = "OfficeSupplies"
    CreditCard = "CreditCard"
    Other = "Other"
