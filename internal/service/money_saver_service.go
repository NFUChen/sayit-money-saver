package service

import (
	"context"
	"log/slog"
)

type MoneySaverService struct {
	TransactionService *TransactionService
	GptService         *GptService
	UserService        *UserService
}

func NewMoneySaverService(
	transactionService *TransactionService,
	gptService *GptService,
	userService *UserService,
) *MoneySaverService {
	return &MoneySaverService{
		TransactionService: transactionService,
		GptService:         gptService,
		UserService:        userService,
	}
}

func (service *MoneySaverService) AddTransaction(ctx context.Context, userName string, prompt string) (*TransactionView, error) {
	user, err := service.UserService.GetUserByUserName(userName)
	if err != nil {
		return nil, err
	}
	view := TransactionView{
		Item: &TransactionItemView{},
	}
	if err := service.GptService.ModelAsk(ctx, &view, prompt); err != nil {
		slog.Error(err.Error())
		return nil, err
	}

	savedTransaction := NewTransaction(user.ID, view)
	_, err = service.TransactionService.AddTransaction(savedTransaction)
	if err != nil {
		return nil, err
	}
	return savedTransaction.View(), nil
}
