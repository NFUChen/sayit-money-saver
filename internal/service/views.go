package service

import (
	"fmt"
	"github.com/google/uuid"
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

// TransactionItemView represents a view model for a transaction item.
type TransactionItemView struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Category    string `json:"category"`
}

// TransactionView represents a view model for a transaction.
type TransactionView struct {
	ID              uuid.UUID            `json:"id,omitempty"`
	TransactionType TransactionType      `json:"transaction_type"`
	Amount          int                  `json:"amount"`
	Item            *TransactionItemView `json:"item"`
}

func (view TransactionView) GetMetaPrompt() string {
	return TransactionViewMetaPrompt
}

func (view TransactionView) Validate() error {
	validTransactions := []TransactionType{
		TransactionTypeExpense,
		TransactionTypeRevenue,
	}
	if view.Item == nil {
		return fmt.Errorf("item can not be nil")
	}

	if len(view.Item.Name) == 0 {
		return fmt.Errorf("item name can not be empty, please insert a valid string")
	}
	if view.Amount <= 0 {
		return fmt.Errorf("amount should be greater than 0, extract from the prompt")
	}
	if !slices.Contains(validTransactions, view.TransactionType) {
		return fmt.Errorf("invalid transaction type: %s", view.TransactionType)
	}

	return nil
}
