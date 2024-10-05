package money

import (
	"fmt"
	"slices"
)

type AssistantActionType string

const (
	AddTransaction AssistantActionType = "AddTransaction"
	Reporting      AssistantActionType = "Reporting"
	Unclear        AssistantActionType = "Unclear"
)

// AssistantActionView represents an action that can be performed by an assistant.
type AssistantActionView struct {
	ActionType AssistantActionType `json:"action_type"`
}

func (view *AssistantActionView) Validate() error {
	validActions := []AssistantActionType{
		AddTransaction,
		Reporting,
		Unclear,
	}
	if !slices.Contains(validActions, view.ActionType) {
		return fmt.Errorf("invalid action type: %s", view.ActionType)
	}
	return nil
}

// TransactionType represents types of transactions.
type TransactionType string

const (
	Expense TransactionType = "Expense"
	Income  TransactionType = "Income"
)

// TransactionItemView represents a view model for a transaction item.
type TransactionItemView struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

// TransactionView represents a view model for a transaction.
type TransactionView struct {
	TransactionType TransactionType     `json:"transaction_type"`
	Amount          int                 `json:"amount"`
	Item            TransactionItemView `json:"item"`
}

func (view *TransactionView) GetMetaPrompt() string {
	return `Potential value for 'transaction_type' key is either 'Expense', or 'Income', please enter one of them.`
}

func (view *TransactionView) Validate() error {
	validTransactions := []TransactionType{
		Expense,
		Income,
	}
	if len(view.Item.Name) == 0 {
		return fmt.Errorf("item name can not be empty, please insert a valid string")
	}
	if view.Amount < 0 {
		return fmt.Errorf("amount can not be negative")
	}
	if !slices.Contains(validTransactions, view.TransactionType) {
		return fmt.Errorf("invalid transaction type: %s", view.TransactionType)
	}

	return nil
}
