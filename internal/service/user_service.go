package service

import (
	. "commit-gpt/internal/server/commons"
	"gorm.io/gorm"
	"log/slog"
)

type UserService struct {
	Engine *gorm.DB
}

func NewUser(
	userName string,
	email string,
	hashedPassword string, role Role,
) *User {
	return &User{
		UserName:       userName,
		Email:          email,
		HashedPassword: hashedPassword,
		Role:           role,
	}
}

func NewUserService(engine *gorm.DB) *UserService {
	return &UserService{Engine: engine}
}

func (service *UserService) GetAllUsers() ([]*User, error) {
	var users []*User
	transaction := service.Engine.Find(&users)
	if transaction.Error != nil {
		slog.Error(transaction.Error.Error())
		return users, transaction.Error
	}
	return users, nil
}

func (service *UserService) CreateUser(user *User) error {
	transaction := service.Engine.Create(user)
	return HandleTransaction(transaction)
}

func (service *UserService) UpdateUser(user *User) error {
	transaction := service.Engine.Model(user).Updates(user)
	return HandleTransaction(transaction)
}

func (service *UserService) DeleteUser(user *User) error {
	transaction := service.Engine.Delete(user)
	return HandleTransaction(transaction)
}

func (service *UserService) GetUserById(id uint) (*User, error) {
	var user User
	transaction := service.Engine.First(&user, id)
	err := HandleTransaction(transaction)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (service *UserService) GetUserByUserName(userName string) (*User, error) {
	var user User
	transaction := service.Engine.Where("user_name = ?", userName).First(&user)
	err := HandleTransaction(transaction)
	if err != nil {
		return nil, err
	}

	return &user, nil
}
