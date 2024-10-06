package service

import (
	"gorm.io/gorm"
	"log/slog"
)

type TransactionService struct {
	Engine      *gorm.DB
	UserService *UserService
}

func NewTransaction(userId int, view TransactionView) *Transaction {
	return &Transaction{
		UserID:          userId,
		TransactionType: view.TransactionType,
		Amount:          view.Amount,
		Item: &TransactionItem{
			Name:         view.Item.Name,
			Description:  view.Item.Description,
			ItemCategory: view.Item.Category,
		},
	}
}

func NewTransactionService(engine *gorm.DB, userService *UserService) *TransactionService {
	return &TransactionService{Engine: engine, UserService: userService}
}

func (service *TransactionService) AddTransaction(transaction *Transaction) (*Transaction, error) {
	transactionResult := service.Engine.Create(&transaction)
	if transactionResult.Error != nil {
		slog.Error(transactionResult.Error.Error())
		return nil, transactionResult.Error
	}

	return transaction, nil
}
