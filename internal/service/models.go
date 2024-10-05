package service

import (
	"github.com/google/uuid"
	"gorm.io/gorm"
	"time"
)

type Platform string
type TransactionType string

const (
	TransactionTypeExpense TransactionType = "expense"
	TransactionTypeRevenue TransactionType = "revenue"
)
const (
	PlatformSelf Platform = "Self"
	PlatformLINE Platform = "LINE"
)

type Role string

const (
	RoleAdmin       Role = "Admin"
	RoleUser        Role = "User"
	RoleGuest       Role = "Guest"
	RoleBlockedUser Role = "BlockedUser"
)

type User struct {
	gorm.Model
	ID             int           `gorm:"primaryKey"`
	UserName       string        `gorm:"not null"`
	Email          string        `gorm:"unique;not null"`
	HashedPassword string        `gorm:"not null"`
	Role           Role          `gorm:"not null"`
	Platform       Platform      `gorm:"not null"`
	ExternalID     *string       `gorm:"column:external_id"`
	Transactions   []Transaction `gorm:"foreignKey:UserID;constraint:OnDelete:CASCADE;"`
}

type Transaction struct {
	ID              uuid.UUID        `gorm:"type:uuid;default:gen_random_uuid();primaryKey"`
	TransactionType TransactionType  `gorm:"not null;index"`
	Amount          int              `gorm:"not null;check:amount >= 0"`
	RecordedDate    time.Time        `gorm:"type:date;default:CURRENT_DATE;index"`
	UserID          *int             `gorm:"index"`
	User            User             `gorm:"constraint:OnDelete:CASCADE;"`
	ItemID          *uuid.UUID       `gorm:"index"`
	Item            *TransactionItem `gorm:"constraint:OnDelete:CASCADE;"`
	CreatedAt       time.Time        `gorm:"autoCreateTime"`
	UpdatedAt       time.Time        `gorm:"autoUpdateTime"`
}

type TransactionItem struct {
	ID           uuid.UUID   `gorm:"type:uuid;default:gen_random_uuid();primaryKey"`
	Name         string      `gorm:"not null"`
	Description  string      `gorm:"not null"`
	ItemCategory string      `gorm:"not null"`
	Transaction  Transaction `gorm:"foreignKey:ItemID;constraint:OnDelete:CASCADE;"`
	UpdatedAt    time.Time   `gorm:"autoUpdateTime"`
}

func GetAllModels() []any {
	return []any{
		User{},
		Transaction{},
		TransactionItem{},
	}
}
