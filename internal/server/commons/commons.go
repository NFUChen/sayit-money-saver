package commons

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
	"log/slog"
)

type HttpHandler struct {
	HttpMethod string
	Path       string
	Handler    gin.HandlerFunc
}

func HandleTransaction(transaction *gorm.DB) error {
	if transaction.Error != nil {
		slog.Error(transaction.Error.Error())
		return transaction.Error
	}
	return nil
}
