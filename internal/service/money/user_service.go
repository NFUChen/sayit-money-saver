package money

import (
	"commit-gpt/internal/service"
	"gorm.io/gorm"
	"log/slog"
)

type UserService struct {
	engine *gorm.DB
}

func (service *UserService) GetAllUsers() ([]*service.User, error) {
	var users []*service.User
	transaction := service.engine.Find(&users)
	if transaction.Error != nil {
		slog.Error(transaction.Error.Error())
		return users, transaction.Error
	}
	return users, nil
}

func (service *UserService) CreateUser(user *service.User) error {
	transaction := service.engine.Create(user)
	if transaction.Error != nil {
		return transaction.Error
	}
	return nil
}
