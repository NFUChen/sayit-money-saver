package api

import (
	"commit-gpt/internal/server/commons"
	"commit-gpt/internal/service"
	"context"
	"github.com/gin-gonic/gin"
	"net/http"
	"time"
)

type LineRouter struct {
	Engine            *gin.Engine
	MoneySaverService *service.MoneySaverService
}

func (router *LineRouter) GetHandlers() []commons.HttpHandler {
	return []commons.HttpHandler{
		{HttpMethod: http.MethodGet, Path: "/ping", Handler: router.pingHandler},
		{HttpMethod: http.MethodPost, Path: "/ask_transaction_text", Handler: router.askTextTransactionHandler},
	}
}

func (router *LineRouter) pingHandler(c *gin.Context) {
	c.JSON(200, gin.H{
		"message": "pong",
	})
}

func (router *LineRouter) askTextTransactionHandler(c *gin.Context) {

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	var body struct {
		Prompt   string `json:"prompt"`
		UserName string `json:"userName"`
	}
	if err := c.ShouldBind(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	transaction, err := router.MoneySaverService.AddTransaction(ctx, body.UserName, body.Prompt)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, transaction)

}
